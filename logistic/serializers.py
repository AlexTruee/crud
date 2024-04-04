from pprint import pprint
from rest_framework import serializers

from logistic.models import Product, StockProduct, Stock

class ProductSerializer(serializers.ModelSerializer):
    # настройте сериализатор для продукта
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']


class ProductPositionSerializer(serializers.ModelSerializer):
    # настройте сериализатор для позиции продукта на складе
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        required=True,
    )
    quantity = serializers.IntegerField(min_value=1, default=1)
    price = serializers.FloatField(min_value=1)

    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    # настройте сериализатор для склада
    class Meta:
        model = Stock
        fields = ['id', 'address', 'positions']

    def create(self, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # создаем склад по его параметрам
        stock = super().create(validated_data)
        # заполняем связанные таблицы
        for position in positions:
            StockProduct.objects.create(stock=stock, product=position['product'],
                                        quantity=position['quantity'], price=position['price'])
        # здесь вам надо заполнить связанные таблицы
        # в нашем случае: таблицу StockProduct
        # с помощью списка positions

        return stock

    def update(self, instance, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # обновляем склад по его параметрам
        stock = super().update(instance, validated_data)

        # здесь вам надо обновить связанные таблицы
        # в нашем случае: таблицу StockProduct
        # с помощью списка positions
        # обновляем связанные таблицы
        for position in positions:
            StockProduct.objects.update_or_create(stock=stock, product=position['product'],
                                                  defaults={'quantity': position['quantity'],
                                                            'price': position['price']})

        return stock
