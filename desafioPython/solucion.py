from abc import ABC, abstractmethod
import re

# Defino mi clase abstracta Operation
class Operation(ABC):
    # Defino el constructor, donde 'config' sirve para configurar
    # diferentes tipos de validaciones
    def __init__(self, field_name, config = {}):
        self.config = config
        self.field_name = field_name

    # Defino el método abstracto operate
    @abstractmethod
    def operate(self, record):
        pass


# Defino la 1era operación heredada
class NormalizeAmountOperation(Operation):
    def operate(self, record):
        val = record.get(self.field_name)
        # Verifico que mi campo no sea nulo
        if (val is None or str(val).strip() == ""):
            record[self.field_name] = None
            return f"WARNING: El campo '{self.field_name}' no existe"
        
        ok = True
        try: 
            raw_val = ""
            # Formateo el valor de mi registro y me aseguro que contenga caracteres válidos
            for c in val:
                if((c >= '0' and c <= '9') or 
                    c == '-' or c == ',' or c == "."):
                    raw_val += c

            # Valor que se registrará al final 
            final_val = raw_val

            # find es el caracter separador de miles de la parte entera
            # e.g. 1,200,322.00 o 1.200.322,00 (ambos formatos son válidos)
            find = ""
            pos_find = -1 # posición de find
            part_whole = ""
            part_decimal = ""

            # si el numero tiene comas y puntos
            both = '.' in raw_val and ',' in raw_val

            # Quito la último coma ',' o punto '.' y trato lo que esté
            # después como la parte decimal
            for i in range(len(raw_val) - 1, -1, -1):
                # Si el ultimo caracter es punto '.'
                if(raw_val[i] == '.'):
                    if(both):
                        part_whole = raw_val[:i] 
                        part_decimal = raw_val[i + 1:]
                        find = ","
                    else:
                        if(raw_val.count(".") > 1): # Es separador de miles
                            part_whole = raw_val
                        else: # Es punto o coma decimal
                            part_whole = raw_val[:i] 
                            part_decimal = raw_val[i + 1:]
                        find = "."
                    pos_find = i
                    break
                # Si el ultimo caracter es coma ','
                if(raw_val[i] == ','):
                    if(both):
                        part_whole = raw_val[:i] 
                        part_decimal = raw_val[i + 1:]
                        find = "."
                    else:
                        if(raw_val.count(",") > 1): # Es separador de miles
                            part_whole = raw_val
                        else: # Es punto o coma decimal
                            part_whole = raw_val[:i] 
                            part_decimal = raw_val[i + 1:]
                        find = ","
                    pos_find = i
                    break

            count = 0
            final_val = ""
            # Verifico que la parte entera cumpla con el formato de separador de miles
            # e.g. 1,200,232: válido        1,220,2: inválido
            raw_part_whole = "" # Aquí guardaré la parte entera (part_whole) sin comas ni puntos
            cant = part_whole.count(find)
            if(cant > 0):
                for c in reversed(part_whole):
                    count = count + 1
                    if(count % 4 == 0):
                        if(c != find and count > 0):
                            ok = False
                    else:
                        raw_part_whole += c
                raw_part_whole = raw_part_whole[::-1]

            else:
                raw_part_whole = part_whole

            
            # Si mi valor original teńia algun punto o coma
            if(pos_find != -1):
                final_val = raw_part_whole + "." + part_decimal
            record[self.field_name] = float(final_val)

        except Exception:
            ok = False
        # Si no se puede convertir 
        if(not ok):
            record[self.field_name] = None
            return f"WARNING: No se pudo convertir '{self.field_name}' correctamente"

# Defino la 2da operación heredada
class ContextualFieldValidation(Operation):
    def operate(self, record):
        req = self.config.get("required") # capturo el parámetro required
        reg = self.config.get("regex")  # capturo el regex simple
        val = record.get(self.field_name) # valor a validar

        if(req):
            if(val is None or str(val).strip() == ""):
                return f"ERROR: El campo '{self.field_name}' no puede ser nulo o vacío"
        if(reg):
            if(not re.fullmatch(reg, str(val))):
                return f"ERROR: El campo '{self.field_name}' no cumple con el patrón regex correcto"
            

class RecordContextManager:
    def __init__(self):
        self.contexts = {}
    # método que registra lista de operaciones
    def register(self, type, list):
        self.contexts[type] = list
    
    # método que procesa registros
    def process_stream(self, record_iterator):
        for record in record_iterator:
            issues = [] # problemas capturados en un registro
            type = record.get("__type__")
            if(not type):
                issues.append("ERROR: El registro no tiene el campo '__type__'")
                yield record, issues
                continue
            operations = self.contexts.get(type, [])
            
            if(not operations): # Si el tipo no tiene operaciones en su contexto
                yield record, issues
                continue
            
            
            for op in operations:
                issue = op.operate(record)
                if(issue is not None):
                    issues.append(issue)

            valid = True
            for issue in issues:
                if issue.startswith("ERROR"): # capturo todos los errores para invalidar
                    valid = False

            # Enrequecimiento de registro
            record["valid"] = valid
            record["issues"] = issues

            yield record, issues


records = [
    #--- Casos ---
    # validos
    # no validos
    {
    "__type__": "order_event",
    "order_id": "ORD789",
    "customer_name": "Luis Vargas",
    "amount": "123,45 EUR",
    "timestamp": "2024-10-26T14:00:00Z"
    },
    {
    "__type__": "order_event",
    "order_id": "ORD100",
    "customer_name": "Bob el Constructor",
    "amount": "no_es_un_numero",
    "timestamp": "2024-13-01T25:61:00Z"
    },
    {
    "__type__": "product_update",
    "product_sku": "SKU_P002",
    "price": None,
    "is_active": "False"
    },
    {
    "__type__": "product_update",
    "product_sku": "SKU_PОO3",
    "price": "25.00",
    # 'is_active'
    },
    {},
]


# Ejemplo de uso
manager = RecordContextManager()

manager.register("order_event", [
    NormalizeAmountOperation(field_name="price"),
    NormalizeAmountOperation(field_name="amount"),
    ContextualFieldValidation(field_name="order_id", config={"required": True}),
    ContextualFieldValidation(field_name="customer_name", 
                              config={
                                "required": True,
                                "regex": r'^[a-zA-Z ]+$'
                              }),
    ContextualFieldValidation(field_name="timestamp", 
                              config={
                                "regex": r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
                              })
])

manager.register("product_update", [
    NormalizeAmountOperation(field_name="price"),
    ContextualFieldValidation(field_name="product_sku", 
                              config = {
                                "required": True,
                                "regex": r'^SKU_.+'
                              }),
    ContextualFieldValidation(field_name="is_active", 
                              config = {
                                "required": True
                              })
])

print("Procesando registros")
for i, (record, issues) in enumerate(manager.process_stream(records), 1):
    print(f"\n{"=" * 5} Datos {"=" * 5}")
    for key, val in record.items():
        print(f"{key} : {val}")


###################
## JUSTIFICACIÓN ##
###################

# 1.
# Usar lista de funciones  puras para cada operación:
# Ventajas:
    # Menos código, quitaríamos la clase abstracta.
    # Más simple de enteder.
# Desventajas
    # Se pierde el polimorfismo, el cual hace que cada vez que se agregan operaciones nuevas no hay necesidad de tocar el 'RecordContextManager', lo cual  cumple con el principio Abierto para extensión y cerrado para modificación. 
    # Se pierde parte de la escalabilidad, ya que antes cada operación podía tener su propio espacio.

# Enfoque basado en eval():
# Ventajas: 
    # Flexible, cualquier lógica que se pueda usar en python, se puede expresar como regla.
    # Menos clases.
# Desventajas:
    # Seguridad, un usuario podría inyectar código malicioso en las reglas.
    # Difícil de debuggear.

# 2.
# Mi código actual si es flexible, ya que usa field_name genérico, asi que se puede usar para cualquier campo (e.g. "salary", "discount", "height", etc).

# Si el campo no existe lo trato con 'if (val is None or str(val).strip() == ""):' y retorno un WARNING.

# Con respecto al estado de registro, esta nunca cambia debido a que 'field_name' y 'config' son fijos. En cambio el estado de registro si llega a cambiar debido a que lo paso como argumento en mi método 'operate(self, record)' y si se modifica 'record[self.field_name] = float(final_val)'
