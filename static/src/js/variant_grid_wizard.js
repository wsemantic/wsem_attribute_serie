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
			this.model.reload(this.handle).then(function() {
				var record = self.model.get(self.handle, {raw: true});
				// Parsea el valor de nombres_tallas desde la cadena JSON a un array de JavaScript
				var nombresTallas = JSON.parse(record.data.nombres_tallas || "[]");
				
				console.log("Nombres de Tallas:", nombresTallas);
				
				// Asegurarse de que el selector apunta correctamente a los elementos de cabecera de tu tabla
				var $tableHeaderThs = $('table.o_list_view thead th');
				console.log("$tableHeaderThs length:", $tableHeaderThs.length); // Verifica que estamos seleccionando elementos
				
				$tableHeaderThs.each(function(index, th) {
					if (index < nombresTallas.length) { // Asegura no salir del rango de nombresTallas
						$(th).text(nombresTallas[index]);
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