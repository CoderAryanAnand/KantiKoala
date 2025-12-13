class ColorPicker {
    constructor() {
        this.modal = document.getElementById('colorPickerModal');
        if (!this.modal) return;

        this.colorArea = document.getElementById('cpColorArea');
        this.colorCursor = document.getElementById('cpColorCursor');
        this.hueSlider = document.getElementById('cpHueSlider');
        this.hueCursor = document.getElementById('cpHueCursor');
        this.resultPreview = document.getElementById('cpResultPreview');
        this.hexInput = document.getElementById('cpHexInput');
        this.rgbDisplay = document.getElementById('cpRgbDisplay');
        
        this.currentInput = null;
        this.currentPreview = null;
        this.currentHexDisplay = null;
        
        this.currentHue = 240;
        this.currentSat = 56;
        this.currentLight = 66;
        this.tempColor = '#667EEA';
        
        this.isDraggingArea = false;
        this.isDraggingHue = false;

        this.initEvents();
    }

    initEvents() {
        // Close buttons
        document.getElementById('cpCloseBtn').addEventListener('click', () => this.close());
        document.getElementById('cpCancelBtn').addEventListener('click', () => this.close());
        document.getElementById('cpConfirmBtn').addEventListener('click', () => this.confirm());
        
        // Close on click outside
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.close();
        });

        // Color Area Interaction
        const startColorDrag = (e) => {
            if (e.cancelable) e.preventDefault();
            this.isDraggingArea = true;
            this.handleColorArea(e);
        };
        this.colorArea.addEventListener('mousedown', startColorDrag);
        this.colorArea.addEventListener('touchstart', startColorDrag, { passive: false });
        this.colorCursor.addEventListener('mousedown', startColorDrag);
        this.colorCursor.addEventListener('touchstart', startColorDrag, { passive: false });

        // Use window for mousemove/mouseup to catch events outside the modal/iframe
        const moveHandler = (e) => {
            if (this.isDraggingArea) {
                if (e.cancelable) e.preventDefault();
                this.handleColorArea(e);
            }
            if (this.isDraggingHue) {
                if (e.cancelable) e.preventDefault();
                this.handleHueSlider(e);
            }
        };
        window.addEventListener('mousemove', moveHandler);
        window.addEventListener('touchmove', moveHandler, { passive: false });

        const endHandler = () => {
            this.isDraggingArea = false;
            this.isDraggingHue = false;
        };
        window.addEventListener('mouseup', endHandler);
        window.addEventListener('touchend', endHandler);

        // Hue Slider Interaction
        const startHueDrag = (e) => {
            if (e.cancelable) e.preventDefault();
            this.isDraggingHue = true;
            this.handleHueSlider(e);
        };
        this.hueSlider.addEventListener('mousedown', startHueDrag);
        this.hueSlider.addEventListener('touchstart', startHueDrag, { passive: false });
        this.hueCursor.addEventListener('mousedown', startHueDrag);
        this.hueCursor.addEventListener('touchstart', startHueDrag, { passive: false });

        // Hex Input
        this.hexInput.addEventListener('input', (e) => {
            const val = e.target.value;
            if (val.match(/^[0-9A-Fa-f]{6}$/)) {
                this.setColorFromHex('#' + val);
            }
        });

        // Presets
        document.querySelectorAll('.cp-preset-color').forEach(preset => {
            preset.addEventListener('click', () => {
                this.setColorFromHex(preset.dataset.color);
            });
        });
    }

    open(inputElement, previewElement, hexDisplayElement) {
        this.currentInput = inputElement;
        this.currentPreview = previewElement;
        this.currentHexDisplay = hexDisplayElement;
        
        this.setColorFromHex(inputElement.value || '#667EEA');
        this.modal.style.display = 'flex';
        this.modal.classList.remove('hidden');
        this.modal.classList.add('flex');
    }

    close() {
        this.modal.style.display = 'none';
        this.modal.classList.add('hidden');
        this.modal.classList.remove('flex');
        this.currentInput = null;
        this.currentPreview = null;
        this.currentHexDisplay = null;
    }

    confirm() {
        if (this.currentInput) {
            this.currentInput.value = this.tempColor;
            this.currentInput.dispatchEvent(new Event('change'));
        }
        if (this.currentPreview) {
            this.currentPreview.style.backgroundColor = this.tempColor;
        }
        // Hex display is now hidden, but we update it anyway if it exists
        if (this.currentHexDisplay) {
            this.currentHexDisplay.textContent = this.tempColor;
        }
        this.close();
    }

    // Color Logic
    hslToRgb(h, s, l) {
        s /= 100;
        l /= 100;
        const a = s * Math.min(l, 1 - l);
        const f = n => {
            const k = (n + h / 30) % 12;
            return l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
        };
        return [Math.round(f(0) * 255), Math.round(f(8) * 255), Math.round(f(4) * 255)];
    }

    rgbToHex(r, g, b) {
        return '#' + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('').toUpperCase();
    }

    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }

    rgbToHsl(r, g, b) {
        r /= 255; g /= 255; b /= 255;
        const max = Math.max(r, g, b), min = Math.min(r, g, b);
        let h, s, l = (max + min) / 2;
        if (max === min) {
            h = s = 0;
        } else {
            const d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
            switch (max) {
                case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
                case g: h = ((b - r) / d + 2) / 6; break;
                case b: h = ((r - g) / d + 4) / 6; break;
            }
        }
        return { h: Math.round(h * 360), s: Math.round(s * 100), l: Math.round(l * 100) };
    }

    updateColorFromHSL() {
        const rgb = this.hslToRgb(this.currentHue, this.currentSat, this.currentLight);
        this.tempColor = this.rgbToHex(rgb[0], rgb[1], rgb[2]);
        
        this.resultPreview.style.backgroundColor = this.tempColor;
        this.hexInput.value = this.tempColor.slice(1);
        this.rgbDisplay.textContent = `RGB: ${rgb[0]}, ${rgb[1]}, ${rgb[2]}`;
    }

    updateColorArea() {
        this.colorArea.style.background = `linear-gradient(to right, #fff, hsl(${this.currentHue}, 100%, 50%))`;
    }

    setColorFromHex(hex) {
        const rgb = this.hexToRgb(hex);
        if (rgb) {
            const hsl = this.rgbToHsl(rgb.r, rgb.g, rgb.b);
            this.currentHue = hsl.h;
            this.currentSat = hsl.s;
            this.currentLight = hsl.l;
            
            // Update Hue Cursor
            const hueX = (this.currentHue / 360) * 100;
            this.hueCursor.style.left = hueX + '%';
            this.hueCursor.style.top = '50%';
            
            // Update Color Cursor
            // Formula: Light = (100 - x/2) * (1 - y/100)
            // Inverse: y = 100 * (1 - Light / (100 - x/2))
            // x is Saturation
            
            const x = this.currentSat;
            let y = 100 * (1 - this.currentLight / (100 - x / 2));
            
            // Clamp values
            y = Math.max(0, Math.min(100, y));
            
            this.colorCursor.style.left = x + '%';
            this.colorCursor.style.top = y + '%';
            
            this.updateColorArea();
            this.updateColorFromHSL();
        }
    }

    handleColorArea(e) {
        if (!this.colorArea || !this.colorCursor) return;
        
        const rect = this.colorArea.getBoundingClientRect();
        const clientX = (e.touches && e.touches.length > 0) ? e.touches[0].clientX : e.clientX;
        const clientY = (e.touches && e.touches.length > 0) ? e.touches[0].clientY : e.clientY;
        
        let x = (clientX - rect.left) / rect.width * 100;
        let y = (clientY - rect.top) / rect.height * 100;
        x = Math.max(0, Math.min(100, x));
        y = Math.max(0, Math.min(100, y));
        
        this.colorCursor.style.left = x + '%';
        this.colorCursor.style.top = y + '%';
        
        this.currentSat = x;
        // Lightness formula matching the visual gradients:
        // (100 - x/2) * (1 - y/100)
        this.currentLight = (100 - x / 2) * (1 - y / 100);
        this.currentLight = Math.max(0, Math.min(100, this.currentLight));
        
        this.updateColorFromHSL();
    }

    handleHueSlider(e) {
        if (!this.hueSlider || !this.hueCursor) return;
        
        const rect = this.hueSlider.getBoundingClientRect();
        const clientX = (e.touches && e.touches.length > 0) ? e.touches[0].clientX : e.clientX;
        
        let x = (clientX - rect.left) / rect.width * 100;
        x = Math.max(0, Math.min(100, x));
        
        this.hueCursor.style.left = x + '%';
        this.hueCursor.style.top = '50%';
        
        this.currentHue = (x / 100) * 360;
        
        this.updateColorArea();
        this.updateColorFromHSL();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.colorPicker = new ColorPicker();
    
    // Delegate click event for dynamically added triggers
    document.body.addEventListener('click', (e) => {
        const trigger = e.target.closest('.color-picker-trigger');
        if (trigger) {
            const inputId = trigger.dataset.inputId;
            const input = document.getElementById(inputId);
            const preview = trigger.querySelector('.color-preview');
            const hexDisplay = trigger.querySelector('.hex-display');
            
            if (window.colorPicker) {
                window.colorPicker.open(input, preview, hexDisplay);
            }
        }
    });
});
