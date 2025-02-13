/** @odoo-module **/

import {registry} from "@web/core/registry";
import {_t} from "@web/core/l10n/translation";
import {useInputField} from "@web/views/fields/input_field_hook";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

import {formatDigitalAddress as digitalAddressFormatter} from "../formatter.esm";

import {Component} from "@odoo/owl";

export class DigitalAdressField extends Component {
    constructor() {
        super(...arguments);
        this.template = "web.DigitalAddressField";
        this.props = {
            ...standardFieldProps,
            placeholder: {type: String, optional: true},
        };
    }

    setup() {
        useInputField({
            getValue: () => this.props.record.data[this.props.name] || "",
            parse: (v) => this.formatDigitalAddress(v),
        });
    }

    // Provide mechanism for end-user to opt out of
    // formatting. The "no format hint" (asterisk)
    // will be removed from the final string.
    formatDigitalAddress(value) {
        if (value.startsWith("*")) {
            return value.substring(1);
        }
        return digitalAddressFormatter(value);
    }
}

export const digitaladdressField = {
    component: DigitalAdressField,
    displayName: _t("Digital Address"),
    supportedTypes: ["char"],
    extractProps: ({attrs}) => ({
        placeholder: attrs.placeholder,
    }),
};

registry.category("fields").add("digital_address", digitaladdressField);
registry.category("formatters").add("digital_address", digitalAddressFormatter);
