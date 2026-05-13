const { localization: { localizationCodes } } = require('/var/opt/kaspersky/ksc-web-console/node_modules/@kl/constants');
console.log('Valid localization keys:');
console.log(Object.keys(localizationCodes));
console.log('Sample entry (en):');
console.log(localizationCodes['en']);
