odoo.define('tu_modulo.VariantGridWizardExtension', function (require) {
    "use strict";

    var FormController = require('web.FormController');

    var VariantGridWizardFormController = FormController.extend({
        _update: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                // Asumiendo que puedes acceder a los datos actualizados de las tallas aquí
                // Este es un pseudocódigo, necesitarías adaptar la lógica para obtener los nombres de las tallas reales
                var talla1Name = self.renderer.state.data.talla_1_nombre || "Talla 1";
                var talla2Name = self.renderer.state.data.talla_2_nombre || "Talla 2";
                var talla3Name = self.renderer.state.data.talla_3_nombre || "Talla 3";

                // Actualiza los encabezados de la tabla con los nuevos nombres
                self.$('.o_list_view thead th[data-name="talla_1"]').text(talla1Name);
                self.$('.o_list_view thead th[data-name="talla_2"]').text(talla2Name);
                self.$('.o_list_view thead th[data-name="talla_3"]').text(talla3Name);
            });
        },
    });

    var viewRegistry = require('web.view_registry');
    viewRegistry.add('variant_grid_wizard_form', VariantGridWizardFormController, 'form');
});
