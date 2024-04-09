odoo.define('wsem_attribute_serie.CustomFieldMany2One', function(require) {
    'use strict';

    var FieldMany2One = require('web.relational_fields').FieldMany2One;
    var fieldRegistry = require('web.field_registry');

    var CustomFieldMany2One = FieldMany2One.extend({
        // Intenta usar _onChange si _setValue no está siendo llamado
        _onChange: function() {
            // Asegúrate de llamar a la implementación original para no perder funcionalidad
            this._super.apply(this, arguments);
            console.log("El campo attribute_serie_id ha cambiado.");
            // Aquí tu lógica adicional...
        },
    });

    fieldRegistry.add('custom_field_many2one_attribute_serie', CustomFieldMany2One);
});


odoo.define('wsem_attribute_serie.CustomFormController', function (require) {
    'use strict';

    var FormController = require('web.FormController');

    FormController.include({
        custom_events: $.extend({}, FormController.prototype.custom_events, {
            attribute_serie_changed: '_onAttributeSerieChanged',
        }),
        _onAttributeSerieChanged: function (e) {
            // Aquí puedes implementar la lógica para actualizar las cabeceras
            // basado en el ID de la serie que se pasó con el evento
            // Podrías necesitar buscar en tu modelo de datos en el cliente para encontrar los nombres correspondientes

            // Esto es un placeholder, necesitarías implementar la lógica específica aquí
            console.log("Serie cambiada a ID:", e.data.serieId);
            // Actualizar las cabeceras según sea necesario
        },
    });
});
