odoo.define('variant_grid_wizard.form', function (require) {
    "use strict";

    var FormController = require('web.FormController');
    var FormView = require('web.FormView');
    var viewRegistry = require('web.view_registry');

    var VariantGridFormController = FormController.extend({
        custom_events: _.extend({}, FormController.prototype.custom_events, {
            field_changed: '_onFieldChanged',
            // Considera añadir otros eventos si son necesarios para tu lógica
        }),

        _onFieldChanged: function (event) {
            var changes = event.data.changes || {};
            if ('attribute_serie_id' in changes || 'line_ids' in changes) {
                // No es necesario llamar a reload aquí si la actualización de los encabezados
                // se maneja a través de _updateTableHeader, que ya maneja la carga.
                this._updateTableHeader();
            }
            this._super.apply(this, arguments);
        },

        // Asegúrate de llamar a _updateTableHeader después de cualquier acción que requiera una actualización
		_updateTableHeader: function() {
			var self = this;
			this.model.reload(this.handle).then(function() {
				var record = self.model.get(self.handle, {raw: true});
				// Parsea el valor de nombres_tallas desde la cadena JSON a un array de JavaScript
				
				var nombresTallas = JSON.parse(record.data.nombres_tallas || "[]");				
				console.log("Nombres de Tallas:", nombresTallas);											
				
				//$('table.o_list_table thead tr th[data-name^="talla_"]').each(function(index) {					
				//	$(this).text(nombresTallas[index] || '');
				//});
				

				$('table.o_list_table thead tr th[data-name^="talla_"]').each(function(index) {
					if (index <= nombresTallas.length) {
						// Si hay un nombre para la talla, actualiza el encabezado y asegura que la columna es visible
						$(this).text(nombresTallas[index]);
						$(this).show();  // Asegura que la columna está visible
					} else {
						// Si no hay nombre para la talla, oculta la columna
						$(this).text('');  // Limpia el texto
						$(this).hide();  // Oculta la columna
					}
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
