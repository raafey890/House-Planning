const materialMarketplace = {

    suppliers: [],

    materialCategories: [

        "Cement",
        "Steel",
        "Paint",
        "Tiles",
        "Electrical"

    ],

    addSupplier(supplier) {

        supplier.id = Date.now();

        supplier.products = [];

        this.suppliers.push(supplier);

    },

    addProduct(supplierId, product) {

        const supplier =
        this.suppliers.find(
            item => item.id === supplierId
        );

        if(supplier) {

            supplier.products.push(product);

        }

    },

    searchProducts(category) {

        return this.suppliers.flatMap(
            supplier =>
            supplier.products.filter(
                product =>
                product.category === category
            )
        );

    }

};

export default materialMarketplace;