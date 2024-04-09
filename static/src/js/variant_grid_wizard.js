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

        _updateTableHeader: function () {
            var attributeSerie = this.model.get(this.handle).data.attribute_serie_id;
            console.log("Selected attribute_serie_id:", attributeSerie);

            if (attributeSerie) {
                var tallaNames = attributeSerie.data.item_ids.data.map(function(item) {
                    return item.data.attribute_value_id.data.display_name;
                });
                console.log("Talla names:", tallaNames);

                var $tableHeader = $('table.o_list_view thead tr');
                $tableHeader.find('th').slice(1).each(function(index) {
                    $(this).text(tallaNames[index] || '');
                });
            }
        },
    });

    var VariantGridFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: VariantGridFormController,
        }),
    });

    viewRegistry.add('variant_grid_wizard_form', VariantGridFormView);
});