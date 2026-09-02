# -*- coding: utf-8 -*-
{
    'name': "wsem_attribute_serie",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Semantic Web Software SL",
    'website': "https://wsemantic.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/18.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '18.0.0.3',

    # any module necessary for this one to work correctly
    'depends': ['sale','purchase','purchase_product_matrix','wsem_pos'],

    'assets': {
    },

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/sec_data.xml'
    ],
    "license": "AGPL-3",
}
