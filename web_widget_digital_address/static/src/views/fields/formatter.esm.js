/** @odoo-module **/

export function formatDigitalAddress(value) {
    const formattedValue = value.replace(/-/g, "");
    const letters = formattedValue.slice(0, 2);
    const divider = Math.floor((formattedValue.length - 2) / 2);
    const firstDigitGroup = formattedValue.slice(2, 2 + divider);
    const lastDigitGroup = formattedValue.slice(2 + divider);
    return `${letters.toUpperCase()}-${firstDigitGroup}-${lastDigitGroup}`;
}
