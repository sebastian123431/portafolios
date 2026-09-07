`synthetic_face.png` es un rostro ficticio generado con la herramienta integrada
ImageGen para pruebas locales. No corresponde a una fotografía de trabajadores.
No se sirve como static ni se carga en la base principal.

Las pruebas ejecutan el detector Haar y el reconocedor LBPH reales, con cambios
de iluminación y compresión JPEG aplicados al dato de prueba. Comprueban el flujo
de identificación y persistencia de asistencia sin mocks; no miden precisión
biométrica sobre personas reales ni verifican una cámara física.

Prompt original:

> Generate a single photorealistic passport-style head-and-shoulders portrait of an entirely fictional adult person who does not resemble any known real person. Purpose: synthetic local software test fixture for an OpenCV frontal-face detector and LBPH recognizer, not a production worker photograph. One face centered, directly facing camera, both eyes clearly visible, neutral expression, short dark hair away from eyes, no facial hair, no glasses, no hat, plain light gray background, even bright diffuse lighting, realistic skin texture, sharp image, face occupies about 60 percent image height. Square composition. No text, no watermark, no extra faces. Save a PNG output suitable for copying into the project's test fixtures.
