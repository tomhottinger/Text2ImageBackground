// Globale Variablen

let selectedSampleImg = null;

let currentFormData = null;



// Initialisierung beim Laden der Seite

window.addEventListener('DOMContentLoaded', function() {

    console.log('Seite geladen, lade Einstellungen...');

    loadSettingsFromUrl();

    

    // Warte kurz bis Form vollständig geladen ist

    setTimeout(() => {

        updateShareUrl();

        console.log('Initiale URL generiert');

    }, 100);

    

    // Event Listener für Formular-Änderungen

    setupEventListeners();

});



// Setup aller Event Listeners

function setupEventListeners() {

    // Update URL bei jeder Änderung

    document.querySelectorAll('#imageForm input, #imageForm select, #imageForm textarea').forEach(elem => {

        elem.addEventListener('change', updateShareUrl);

        elem.addEventListener('input', updateShareUrl);

    });

    

    // Bild-Upload Handler

    document.getElementById('imageFile').addEventListener('change', function() {

        if (this.files.length > 0) {

            // Clear sample selection

            document.querySelectorAll('.sample-images img').forEach(i => i.classList.remove('selected'));

            document.getElementById('selectedSample').value = '';

            selectedSampleImg = null;

            // URL-Box ausblenden bei Upload

            document.getElementById('urlBox').style.display = 'none';

        }

    });

    

    // Form Submit Handler

    document.getElementById('imageForm').addEventListener('submit', handleFormSubmit);

    

    // Download Button Handler

    document.getElementById('downloadBtn').addEventListener('click', handleDownload);

}



// Lade Einstellungen aus URL-Parametern

function loadSettingsFromUrl() {

    const params = new URLSearchParams(window.location.search);

    

    if (params.has('font_name')) document.getElementById('font_name').value = params.get('font_name');

    if (params.has('font_size')) document.getElementById('font_size').value = params.get('font_size');

    if (params.has('text_color')) document.getElementById('text_color').value = params.get('text_color');

    if (params.has('position')) document.getElementById('position').value = params.get('position');

    if (params.has('text_align')) document.getElementById('text_align').value = params.get('text_align');

    if (params.has('x_offset')) document.getElementById('x_offset').value = params.get('x_offset');

    if (params.has('y_offset')) document.getElementById('y_offset').value = params.get('y_offset');

    

    if (params.has('bg_color')) document.getElementById('bg_color').value = params.get('bg_color');

    if (params.has('bg_opacity')) {

        const val = params.get('bg_opacity');

        document.getElementById('bg_opacity').value = val;

        document.getElementById('opacityValue').textContent = val;

    }

    if (params.has('bg_blur')) {

        const val = params.get('bg_blur');

        document.getElementById('bg_blur').value = val;

        document.getElementById('blurValue').textContent = val;

    }

    if (params.has('bg_radius')) document.getElementById('bg_radius').value = params.get('bg_radius');

    if (params.has('bg_padding')) document.getElementById('bg_padding').value = params.get('bg_padding');

    if (params.has('box_width_percent')) {

        const val = params.get('box_width_percent');

        document.getElementById('box_width_percent').value = val;

        document.getElementById('widthValue').textContent = val + '%';

    }

    

    // Wenn Sample-Bild in URL

    if (params.has('sample')) {

        const sampleName = params.get('sample');

        document.getElementById('selectedSample').value = sampleName;

        const sampleImg = document.querySelector(`[data-name="${sampleName}"]`);

        if (sampleImg) {

            sampleImg.classList.add('selected');

            selectedSampleImg = sampleName;

        }

    }

}



// Generiere Share-URL mit aktuellen Einstellungen

function updateShareUrl() {

    const form = document.getElementById('imageForm');

    if (!form) {

        console.error('Form nicht gefunden!');

        return;

    }

    

    const formData = new FormData(form);

    const params = new URLSearchParams();

    

    // Alle Parameter außer Bild und Text

    const fontName = formData.get('font_name');

    if (fontName) params.set('font_name', fontName);

    

    params.set('font_size', formData.get('font_size') || '40');

    params.set('text_color', formData.get('text_color') || '#FFFFFF');

    params.set('position', formData.get('position') || 'center');

    params.set('text_align', formData.get('text_align') || 'center');

    params.set('x_offset', formData.get('x_offset') || '0');

    params.set('y_offset', formData.get('y_offset') || '0');

    params.set('bg_color', formData.get('bg_color') || '#000000');

    params.set('bg_opacity', formData.get('bg_opacity') || '128');

    params.set('bg_blur', formData.get('bg_blur') || '10');

    params.set('bg_radius', formData.get('bg_radius') || '15');

    params.set('bg_padding', formData.get('bg_padding') || '20');

    params.set('box_width_percent', formData.get('box_width_percent') || '80');

    

    // Sample-Bild wenn ausgewählt

    const sampleImage = formData.get('sample_image');

    if (sampleImage) {

        params.set('sample', sampleImage);

    }

    

    const url = window.location.origin + window.location.pathname + '?' + params.toString();

    

    // Update beide URL-Felder

    const shareUrlElem = document.getElementById('shareUrl');

    const settingsUrlElem = document.getElementById('settingsUrlBox');

    

    if (shareUrlElem) shareUrlElem.value = url;

    if (settingsUrlElem) settingsUrlElem.value = url;

    

    const urlBoxElem = document.getElementById('urlBox');

    if (urlBoxElem) urlBoxElem.style.display = 'block';

    

    console.log('URL generiert:', url);

}



// Sample-Bild auswählen

function selectSample(img) {

    // Deselect all

    document.querySelectorAll('.sample-images img').forEach(i => i.classList.remove('selected'));

    // Select clicked

    img.classList.add('selected');

    selectedSampleImg = img.dataset.name;

    document.getElementById('selectedSample').value = selectedSampleImg;

    // Clear file input

    document.getElementById('imageFile').value = '';

    

    updateShareUrl();

}



// Form Submit Handler

async function handleFormSubmit(e) {

    e.preventDefault();

    

    const formData = new FormData(this);

    currentFormData = formData;

    

    document.getElementById('loading').style.display = 'block';

    document.getElementById('preview').style.display = 'none';



    try {

        const response = await fetch('/process', {

            method: 'POST',

            body: formData

        });



        if (!response.ok) {

            throw new Error('Fehler bei der Verarbeitung');

        }



        const blob = await response.blob();

        const url = URL.createObjectURL(blob);



        // Preview anzeigen

        document.getElementById('previewImg').src = url;

        document.getElementById('preview').style.display = 'block';

        

        // Update Share URL

        updateShareUrl();



    } catch (error) {

        console.error('Form Submit Error:', error);

        alert('Fehler: ' + error.message);

    } finally {

        document.getElementById('loading').style.display = 'none';

    }

}



// Download Button Handler

async function handleDownload() {

    if (!currentFormData) {

        alert('Bitte erst eine Vorschau erstellen!');

        return;

    }



    try {

        const previewImg = document.getElementById('previewImg');

        const response = await fetch(previewImg.src);

        const blob = await response.blob();

        

        const a = document.createElement('a');

        a.href = URL.createObjectURL(blob);

        a.download = 'image_with_text.jpg';

        document.body.appendChild(a);

        a.click();

        document.body.removeChild(a);

    } catch (error) {

        console.error('Download Error:', error);

        alert('Download-Fehler: ' + error.message);

    }

}



// URL kopieren (obere Box)

function copyUrl() {

    const urlInput = document.getElementById('shareUrl');

    

    if (navigator.clipboard) {

        navigator.clipboard.writeText(urlInput.value).then(() => {

            showUrlBoxFeedback();

        }).catch((err) => {

            console.error('Clipboard Error:', err);

            fallbackCopy(urlInput);

        });

    } else {

        fallbackCopy(urlInput);

    }

}



function fallbackCopy(input) {

    input.select();

    input.setSelectionRange(0, 99999);

    try {

        document.execCommand('copy');

        showUrlBoxFeedback();

    } catch (err) {

        console.error('Copy failed:', err);

        alert('Kopieren fehlgeschlagen. Bitte manuell kopieren.');

    }

}



function showUrlBoxFeedback() {

    const btn = event.target;

    if (!btn) return;

    

    const originalText = btn.textContent;

    btn.textContent = '✅ Kopiert!';

    btn.style.background = 'linear-gradient(135deg, #20c997 0%, #17a2b8 100%)';

    

    setTimeout(() => {

        btn.textContent = originalText;

        btn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';

    }, 2000);

}



// URL kopieren (untere Collapsible Box)

function copySettingsUrl() {

    const urlBox = document.getElementById('settingsUrlBox');

    

    // Sicherstellen dass URL aktuell ist

    updateShareUrl();

    

    if (!urlBox.value) {

        alert('Keine URL vorhanden. Bitte warte einen Moment.');

        return;

    }

    

    if (navigator.clipboard) {

        navigator.clipboard.writeText(urlBox.value).then(() => {

            showSettingsUrlFeedback();

        }).catch((err) => {

            console.error('Clipboard Error:', err);

            fallbackCopySettings(urlBox);

        });

    } else {

        fallbackCopySettings(urlBox);

    }

}



function fallbackCopySettings(urlBox) {

    urlBox.select();

    urlBox.setSelectionRange(0, 99999);

    try {

        document.execCommand('copy');

        showSettingsUrlFeedback();

    } catch (err) {

        console.error('Copy failed:', err);

        alert('Kopieren fehlgeschlagen. Bitte manuell kopieren.');

    }

}



function showSettingsUrlFeedback() {

    const btn = event.target;

    if (!btn) return;

    

    const originalText = btn.innerHTML;

    btn.innerHTML = '✅ URL kopiert!';

    btn.style.background = 'linear-gradient(135deg, #20c997 0%, #17a2b8 100%)';

    

    setTimeout(() => {

        btn.innerHTML = originalText;

        btn.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';

    }, 2000);

}
