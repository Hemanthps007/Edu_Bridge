// EduBridge — Biometric Face ID Authentication & Profile Enrollment

function startFaceLogin() {
  const alpine = Alpine.$data(document.querySelector('[x-data]'));
  const video = document.getElementById('faceVideo');
  if (!alpine || !video) return;

  alpine.faceError = '';
  alpine.statusText = 'Starting webcam...';

  window.faceAuth.loadModels(msg => { alpine.statusText = msg; })
    .then(() => window.faceAuth.startCamera(video))
    .then(() => {
      alpine.cameraActive = true;
      alpine.statusText = 'Face centered. Click Verify.';
    })
    .catch(err => {
      alpine.cameraActive = false;
      alpine.faceError = err.message || 'Unable to access camera.';
    });
}

async function captureAndVerify() {
  const alpine = Alpine.$data(document.querySelector('[x-data]'));
  const emailInput = document.getElementById('faceEmail');
  if (!alpine || !emailInput) return;

  const email = emailInput.value.trim();
  if (!email) {
    alpine.faceError = 'Please enter your registered email address first.';
    return;
  }

  alpine.isVerifying = true;
  alpine.faceError = '';
  alpine.statusText = 'Extracting facial landmark vector...';

  try {
    const descriptor = await window.faceAuth.extractDescriptor();
    if (!descriptor) {
      throw new Error('No face detected. Please center your face in good lighting.');
    }

    alpine.statusText = 'Comparing biometric signatures...';

    const resp = await fetch('/verify-face/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email, descriptor: descriptor })
    });
    const data = await resp.json();

    if (data.success) {
      alpine.statusText = 'Biometrics matched! Redirecting...';
      window.location.href = data.redirect || '/dashboard/';
    } else {
      alpine.faceError = data.error || 'Face verification failed.';
      alpine.statusText = 'Mismatch detected.';
    }
  } catch (err) {
    alpine.faceError = err.message || 'Error processing face verification.';
  } finally {
    alpine.isVerifying = false;
  }
}

function startEnrollmentCamera() {
  const alpine = Alpine.$data(document.querySelector('[x-data]'));
  const video = document.getElementById('enrollVideo');
  if (!alpine || !video) return;

  alpine.enrollError = '';
  alpine.enrollSuccess = '';
  alpine.statusText = 'Starting camera...';

  window.faceAuth.loadModels(msg => { alpine.statusText = msg; })
    .then(() => window.faceAuth.startCamera(video))
    .then(() => {
      alpine.cameraActive = true;
      alpine.statusText = 'Camera ready. Hold steady.';
    })
    .catch(err => {
      alpine.cameraActive = false;
      alpine.enrollError = err.message || 'Could not start camera.';
    });
}

async function enrollFaceDescriptors() {
  const alpine = Alpine.$data(document.querySelector('[x-data]'));
  if (!alpine) return;

  alpine.isEnrolling = true;
  alpine.enrollError = '';
  alpine.statusText = 'Capturing 3 facial samples...';

  try {
    const template = await window.faceAuth.captureEnrollmentTemplate(3, (cur, total) => {
      alpine.statusText = `Capturing sample ${cur} of ${total}...`;
    });

    alpine.statusText = 'Encrypting & storing biometrics...';

    const resp = await fetch('/enroll-face/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ descriptor: template })
    });
    const res = await resp.json();

    if (res.success) {
      alpine.enrollSuccess = 'Face ID enrolled successfully! +150 XP awarded.';
      alpine.statusText = 'Enrolled.';
      setTimeout(() => window.location.reload(), 1500);
    } else {
      alpine.enrollError = res.error || 'Biometric enrollment failed.';
    }
  } catch (err) {
    alpine.enrollError = err.message || 'Error capturing facial samples.';
  } finally {
    alpine.isEnrolling = false;
  }
}

async function deleteFaceBiometrics() {
  if (!confirm('Are you sure you want to permanently delete your enrolled face biometrics?')) return;
  const resp = await fetch('/delete-face/', { method: 'POST', headers: {'Content-Type': 'application/json'} });
  const res = await resp.json();
  if (res.success) {
    window.location.reload();
  }
}
