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
                this._updateTableHeader();
            }
            this._super.apply(this, arguments);
        },

		_updateTableHeader: function() {
			var self = this;
			// Se fuerza la recarga del registro actual para asegurarse de que los datos estén actualizados
			this.model.reload(this.handle).then(function() {
				var record = self.model.get(self.handle, {raw: true});
				// Suponiendo que nombres_tallas ya está almacenado como un string JSON válido
				var nombresTallas;
				try {
					nombresTallas = JSON.parse(record.data.nombres_tallas || "[]");
				} catch(e) {
					console.error("Error parsing nombres_tallas:", e);
					nombresTallas = []; // Fallback a un array vacío en caso de error
				}
				
				console.log("Nombres de Tallas:", nombresTallas);
				
				// Actualiza las cabeceras de las columnas con los nombres de las tallas
				$('table.o_list_view thead tr th[data-name^="talla_"]').each(function(index) {
					// Se actualiza el texto de cada cabecera de columna con los nombres de las tallas
					$(this).text(nombresTallas[index] || '');
				});
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