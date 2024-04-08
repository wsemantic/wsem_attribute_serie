odoo.define('wsem_attribute_serie.CustomFieldMany2One', function(require) {
    'use strict';

    var core = require('web.core');
    var relational_fields = require('web.relational_fields');
    var FieldMany2One = relational_fields.FieldMany2One;
    var fieldRegistry = require('web.field_registry');

    var CustomFieldMany2One = FieldMany2One.extend({
        // Sobreescribe el método que se dispara después de que un valor es seleccionado
        _setValue: function (value, options) {
            // Primero, ejecuta la lógica original para asegurarte de que el valor se establece correctamente
			console.log("Set value llamado")
            return this._super.apply(this, arguments).then(() => {
                // Después de establecer el valor, dispara un evento personalizado
                // con el valor seleccionado (puede ser el ID de la serie seleccionada)
                this.trigger_up('attribute_serie_changed', {serieId: value});
            });
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
