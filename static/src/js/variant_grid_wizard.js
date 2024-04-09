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
            // Tu lógica existente
            this._super.apply(this, arguments);
        },

        // Asegúrate de llamar a _updateTableHeader después de cualquier acción que requiera una actualización
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

        // Reincorporando reload con un control más refinado
        reload: function() {
            var self = this;
            return this._super.apply(this, arguments).then(function() {
                self._updateTableHeader(); // Llama a actualizar los encabezados después de recargar
            });
        },

        // Un ejemplo de cómo podrías manejar el evento de añadir una nueva línea.
        // Esto dependerá de cómo estés añadiendo nuevas líneas en tu interfaz
        _onAddLine: function() {
            // Posiblemente necesites una lógica aquí para manejar específicamente la adición de nuevas líneas
            this.reload(); // Esto recargará y luego actualizará los encabezados
        },

    });

    var VariantGridFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: VariantGridFormController,
        }),
    });

    viewRegistry.add('variant_grid_wizard_form', VariantGridFormView);
});
