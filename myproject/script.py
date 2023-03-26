import os
import django
import random
import string
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import Product, Warehouse, WarehouseProduct, Customer, CustomerProduct


def random_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))


def generate_market(num_products, num_warehouses):
    products = [Product.objects.create(name=f'T{i + 1}') for i in range(num_products)]
    warehouses = [Warehouse.objects.create(name=f'C{i + 1}') for i in range(num_warehouses)]

    for warehouse in warehouses:
        for product in random.sample(products, random.randint(1, num_products)):
            WarehouseProduct.objects.create(
                warehouse=warehouse,
                product=product,
                storage_limit=random.randint(10, 100),
                storage_rate=random.uniform(1, 10)
            )


def generate_customers(num_customers, num_products):
    customers = [Customer.objects.create(name=f'K{i + 1}') for i in range(num_customers)]

    for customer in customers:
        products = list(Product.objects.all())
        for product in random.sample(products, random.randint(1, num_products)):
            CustomerProduct.objects.create(
                customer=customer,
                product=product,
                quantity=random.randint(1, 50)
            )


def transport_cost(quantity, distance, transport_rate):
    return quantity * distance * transport_rate


def find_optimal_options(num_iterations, transport_rate):
    for _ in range(num_iterations):
        # generate a client with a random set of goods
        customer = Customer.objects.create(name=f'K{Customer.objects.count() + 1}')
        products = list(Product.objects.all())
        for product in random.sample(products, random.randint(1, len(products))):
            CustomerProduct.objects.create(
                customer=customer,
                product=product,
                quantity=random.randint(1, 50)
            )

        best_cheapest = {}
        best_convenient = {}

        # calculate the optimal options for each product of the client
        for customer_product in CustomerProduct.objects.filter(customer=customer):
            product = customer_product.product
            quantity = customer_product.quantity

            cheapest_option = None
            convenient_option = None
            min_cheapest_cost = float('inf')
            min_convenient_cost = float('inf')

            for warehouse_product in WarehouseProduct.objects.filter(product=product):
                warehouse = warehouse_product.warehouse
                distance = random.uniform(1, 100)

                # calculate the cost of transportation
                transport_costs = transport_cost(quantity, distance, transport_rate)

                total_cost = Decimal(str(transport_costs)) + warehouse_product.storage_rate * quantity

                # updating the best options
                if total_cost < min_cheapest_cost:
                    min_cheapest_cost = total_cost
                    cheapest_option = {
                        'warehouse': warehouse,
                        'cost': total_cost,
                        'transport_costs': transport_costs
                    }

                if warehouse_product.storage_limit >= quantity and (
                        convenient_option is None or total_cost < min_convenient_cost):
                    min_convenient_cost = total_cost
                    convenient_option = {
                        'warehouse': warehouse,
                        'cost': total_cost,
                        'transport_costs': transport_costs
                    }

            best_cheapest[product] = cheapest_option
            best_convenient[product] = convenient_option

        print(f'Клиент {customer.name}:')
        for customer_product in CustomerProduct.objects.filter(customer=customer):
            product = customer_product.product
            quantity = customer_product.quantity
            print(f'  Товар {product.name}: {quantity} шт.')

        print('\nОптимальные варианты:')
        print('  Самый дешевый:')
        for product, option in best_cheapest.items():
            if option is None:
                print(f'Для товара {product.name} не удалось найти вариант хранения')
            else:
                print(
                    f'Товар {product.name}: Склад {option["warehouse"].name}, стоимость {option["cost"]:.2f} у.е. (транспортировка: {option["transport_costs"]:.2f} у.е.)')

        print('  Самый удобный:')
        for product, option in best_convenient.items():
            if option is None:
                print(f'Для товара {product.name} не удалось найти вариант хранения')
            else:
                print(
                    f'Товар {product.name}: Склад {option["warehouse"].name}, стоимость {option["cost"]:.2f} у.е. (транспортировка: {option["transport_costs"]:.2f} у.е.)')

        print('\n')


def main():
    num_products = 20
    num_warehouses = 50
    num_customers = 100
    num_iterations = 10
    transport_rate = 0.01

    # generate goods, warehouses and customers
    generate_market(num_products, num_warehouses)
    generate_customers(num_customers, num_products)

    # find the best options for clients
    find_optimal_options(num_iterations, transport_rate)


if __name__ == '__main__':
    main()
