odoo.define('variant_grid_wizard.form', function (require) {
    "use strict";

    var FormController = require('web.FormController');
    var FormView = require('web.FormView');
    var viewRegistry = require('web.view_registry');

    var VariantGridFormController = FormController.extend({
        custom_events: _.extend({}, FormController.prototype.custom_events, {
            field_changed: '_onFieldChanged',
        }),

        _onFieldChanged: function (event) {
            var changes = event.data.changes || {};
            if ('attribute_serie_id' in changes) {
                // No es necesario llamar a reload aquí si la actualización de los encabezados
                // se maneja a través de _updateTableHeader, que ya maneja la carga.
                this._updateTableHeader();
            }
            this._super.apply(this, arguments);
        },

        _updateTableHeader: function() {
            var self = this;
            // Al remover reload, asegurarse de que los cambios en nombres_tallas se reflejen
            // directamente sin recargar todo el formulario.
            var record = self.model.get(self.handle, {raw: true});
            var nombresTallas = JSON.parse(record.data.nombres_tallas || "[]");

            console.log("Nombres de Tallas:", nombresTallas);

            $('table.o_list_table thead tr th[data-name^="talla_"]').each(function(index) {
                // Se actualiza el texto de cada cabecera de columna con los nombres de las tallas
                $(this).text(nombresTallas[index] || '');
            });
        },

        // Se sobreescribe el método saveRecord para manejar la actualización de las cabeceras
        // después de añadir una nueva línea, ya que este evento también podría requerir recargar
        // los nombres de tallas.
        saveRecord: function() {
            var self = this;
            // Llama primero al método saveRecord original para asegurar que se guarden los cambios.
            return this._super.apply(this, arguments).then(function () {
                // Después de guardar, actualiza las cabeceras para reflejar cualquier cambio.
                self._updateTableHeader();
            });
        },

    });

    var VariantGridFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: VariantGridFormController,
        }),
    });

    viewRegistry.add('variant_grid_wizard_form', VariantGridFormView);
});
