odoo.define('variant_grid_wizard.form', function (require) {
    "use strict";

    var FormController = require('web.FormController');
    var FormView = require('web.FormView');
    var viewRegistry = require('web.view_registry');

    var VariantGridFormController = FormController.extend({
        custom_events: _.extend({}, FormController.prototype.custom_events, {
            field_changed: '_onFieldChanged',
        }),

        // Este método maneja el evento field_changed
        _onFieldChanged: function (event) {
            var changes = event.data.changes || {};
            // Verifica si el cambio ocurrió en attribute_serie_id
            if ('attribute_serie_id' in changes) {
                // Llama a _updateTableHeader para actualizar los encabezados
                this._updateTableHeader();
            }
            // Asegúrate de llamar al método super para no interrumpir la cadena de eventos
            this._super.apply(this, arguments);
        },

        // Actualiza los encabezados de las columnas basándose en los valores de nombres_tallas
        _updateTableHeader: function() {
            var self = this;
            // Obtiene el registro actual para acceder a los datos del modelo
            var record = self.model.get(self.handle, {raw: true});
            // Parsea los nombres de tallas desde el campo nombres_tallas
            var nombresTallas = JSON.parse(record.data.nombres_tallas || "[]");

            console.log("Nombres de Tallas:", nombresTallas);

            // Actualiza los textos de los encabezados en el DOM
            $('table.o_list_table thead tr th[data-name^="talla_"]').each(function(index) {
                if (index < nombresTallas.length) {
                    $(this).text(nombresTallas[index] || '');
                }
            });
        },
    });

    // Extendemos FormView para utilizar nuestro FormController personalizado
    var VariantGridFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: VariantGridFormController,
        }),
    });

    // Registramos nuestra vista personalizada para que esté disponible en Odoo
    viewRegistry.add('variant_grid_wizard_form', VariantGridFormView);
});
