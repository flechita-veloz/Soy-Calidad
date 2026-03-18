Productos = {1:'Pantalones', 2:'Camisas', 3:'Corbatas', 4:'Casacas'}
Precios = {1:200.00, 2:120.00, 3:50.00, 4:350.00}
Stock = {1:50, 2:45, 3:30, 4:15}

# ========================================
# Lista de Productos:
# ========================================
# 1 	 Pantalones	 200.0 	 50
# 2 	 Camisas 	 120.0 	 45
# 3 	 Corbatas 	 50.0 	 30
# 4 	 Casacas 	 350.0 	 15
# ========================================
# [1] Agregar, [2] Eliminar, [3] Actualizar, [4] Salir
# Elija opción:

def buscarProducto(search):
    for key, value in Productos.items():
        if(value == search):
            return key
    return -1
while(1):
    print("\n" * 3)
    print("="*80)
    print("Lista de Productos")
    print("="*80)

    for key in Productos:
        print(f"{key:<5}\t"
            f"{Productos[key]:<30}\t"
            f"{Precios[key]:<15}\t"
            f"{Stock[key]:<10}")
    print("="*80)
    print("[1] Agregar, [2] Eliminar, [3] Actualizar, [4] Salir")
    opt = int(input("Elija opción: "))
    if(opt < 1 or opt > 4):
        print("\nIngrese un número válido por favor")
    else:
        if(opt == 1):
            nombre = input("Ingrese el nombre del producto: ")
            precio = input("Ingrese el precio del producto: ")
            stock = input("Ingrese el stock del producto: ")
            newKey = len(Productos) + 1
            Productos[newKey] = nombre
            Precios[newKey] = precio
            Stock[newKey] = stock
            print("Producto agregado correctamente")
        elif(opt == 2):
            nombre = input("Ingrese el nombre del producto que quiero eliminar: ")
            key = buscarProducto(nombre)
            if(key == -1):
                print("\nNo existe el producto ingresado")
            else:
                del Productos[key]
                del Precios[key]
                del Stock[key]
                print("\nProducto eliminado correctamente")
        elif(opt == 3):
            nombre = input("Ingrese el nombre del producto que quiere actualizar: ")
            key = buscarProducto(nombre)
            if(key == -1):
                print("\nNo existe el producto ingresado")
            else:
                nombre = input("Ingrese el nuevo nombre del producto: ")
                precio = input("Ingrese el nuevo precio del producto: ")
                stock = input("Ingrese el nuevo stock del producto: ")
                Productos[key] = nombre
                Precios[key] = precio
                Stock[key] = stock
                print("\nProducto actualizado correctamente")
        else:
            print("\nSaliendo del programa")
            break

    
