odoo.define('wsem_attribute_serie.CustomFieldMany2One', function (require) {
"use strict";

    var FieldMany2One = require('web.relational_fields').FieldMany2One;
    var fieldRegistry = require('web.field_registry');

    var CustomFieldMany2One = FieldMany2One.extend({
        // Sobreescribe el método _onChange para ejecutar lógica personalizada
        _onChange: function () {
            this._super.apply(this, arguments);  // Llama a la implementación original
            // Aquí va tu lógica personalizada que quieres ejecutar cuando cambia el campo
            console.log("El campo attribute_serie_id ha cambiado.");
        },
    });

    fieldRegistry.add('custom_field_many2one', CustomFieldMany2One);
});
