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
            var self = this;
            var changes = event.data.changes || {};
            // Verifica si el cambio ocurrió en 'attribute_serie_id' o se añadieron líneas
            if ('attribute_serie_id' in changes || 'line_ids' in changes) {
                // Aquí incorporamos la llamada a reload antes de actualizar la cabecera
                this.reload().then(function() {
                    // Una vez recargado, actualiza las cabeceras.
                    self._updateTableHeader();
                });
            }
            this._super.apply(this, arguments);
        },

        _updateTableHeader: function() {
            // Esta función se mantiene como estaba, actualizando las cabeceras de la tabla
            var self = this;
            var record = self.model.get(self.handle, {raw: true});
            var nombresTallas = JSON.parse(record.data.nombres_tallas || "[]");

            console.log("Nombres de Tallas:", nombresTallas);

            $('table.o_list_table thead tr th[data-name^="talla_"]').each(function(index) {
                if (index < nombresTallas.length) {
                    $(this).text(nombresTallas[index] || '');
                }
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
