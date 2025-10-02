# TODO List for Aligning Frontend and Backend

## Backend Cleanup
- [x] Remove venv/app.py to avoid confusion with old backend code

## Frontend Updates (templates/index.html)
- [x] Update URL check button onclick to call scanURL()
- [x] Update QR upload button onclick to call scanQR()
- [x] Add onclick to startScanBtn for real-time scanning

## JavaScript Updates (static/js/script.js)
- [x] Update scanURL() to call /check_url with JSON {url}
- [x] Update scanQR() to convert file to base64 and send JSON {image: base64} to /scan_qr
- [x] Implement real-time scanning: use getUserMedia, capture video frames as base64, send to /scan_qr_realtime
- [x] Update showResult() to handle backend response: safe/unsafe, no_qr, analysis details

## Testing
- [ ] Test URL scanning functionality
- [ ] Test QR code upload scanning
- [ ] Test real-time QR scanning
- [ ] Verify UI displays correct results from backend
