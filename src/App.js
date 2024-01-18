import React, { useState, useRef, useCallback } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [userEmail, setUserEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loggedIn, setLoggedIn] = useState(false);
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState("");
  const [uploadStatus, setUploadStatus] = useState("idle");
  const fileInputRef = useRef(null);
  const isUploadDisabled = !loggedIn || uploadStatus !== "idle";
  const [isConfirming, setIsConfirming] = useState(false);
  const [confirmMessage, setConfirmMessage] = useState('');
  const [confirmationCode, setConfirmationCode] = useState('');
  const [isFileDraggedOver, setIsFileDraggedOver] = useState(false);

  const handleLoginSignup = async () => {
    try {
      const response = await axios.post('/login-signup', { userEmail, password });
      const data = response.data;
      console.log(data.status)
      if (data.status === 'login_success') {
        setLoggedIn(true);
      } else if (data.status === 'signup_in_progress') {
        setIsConfirming(true);
        setConfirmMessage('Please check your email for the confirmation code.');
      } else {
        alert('Login/Signup failed.');
      }
    } catch (error) {
      console.error('Login/Signup error:', error);
    }
  };

  const handleConfirmCode = async () => {
    try {
      const code = parseInt(confirmationCode, 10); // Convert to integer with base 10
      if (isNaN(code)) { // Check if the conversion results in an actual number
        alert("Please enter a valid numeric code.");
        return;
      } else if (code < 100000 || code > 999999) {
        alert("Please enter a 6-digit numeric code.");
        return;
      }
      console.log("just after checking confirmation code");
      const response = await axios.post('/confirm', { userEmail, confirmationCode: code });
      const data = response.data;
      console.log("just before checking confirmation success");
      if (data.status === 'confirmation_success') {
        setLoggedIn(true);
        setIsConfirming(false);
        setConfirmationCode('');
      } else {
        setLoggedIn(false);
        setIsConfirming(false);
        setConfirmationCode('');
        if (data.status === 'confirmation_failed_timeout') alert('Confirmation timed out after 5 minutes. Please sign up again.');
        else if (data.status === 'confirmation_failed') alert('Confirmation code wrong. Please sign up again.');
        else alert('User not found. Please sign up again.');
      }
    } catch (error) {
      console.error('Confirmation error:', error);
    }
  };

  const handleLogout = () => {
    // If using JWT, remove the token
    // localStorage.removeItem('token');
    setLoggedIn(false);
    setUserEmail('');
    setPassword('');
    setUploadStatus('idle');
    // Reset other states as necessary
  };

  const handleFileSelect = (event) => {
    const newFile = event.target.files[0];
    if (newFile) {
      setFile(newFile);
      setUploadStatus("selected"); // Set to 'selected' when a file is chosen
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current.click(); // Open the file dialog
  };

  const checkSummaryStatus = useCallback(async (filename) => {
    try {
      const statusResponse = await axios.get(`/status/${filename}`);
      if (statusResponse.data.status === 'completed') {
        setSummary(statusResponse.data.summary);
        setUploadStatus("completed"); 
        setUploadStatus('idle'); // Set to idle if credit is still available for more summaries
      } else if (statusResponse.data.status === 'processing') {
        setTimeout(() => checkSummaryStatus(filename), 5000); // Poll every 5 seconds
      } else if (statusResponse.data.status === 'error') {
        setUploadStatus("error");
      }
    } catch (error) {
      console.error('Error checking summary status:', error);
      setUploadStatus("error");
    }
  }, []);
  
  const handleUpload = useCallback(async () => {
    if (file && uploadStatus === "selected") {
      const formData = new FormData();
      formData.append('file', file);
      setUploadStatus("uploading");
      try {
        const uploadResponse = await axios.post('/upload', formData);
        if (uploadResponse.data.status === 'uploaded') {
          setUploadStatus("uploaded");  // File is uploaded but not yet summarized
          checkSummaryStatus(uploadResponse.data.filename);
        }
      } catch (error) {
        console.error('Error uploading file:', error);
        setUploadStatus("error");
      }
    }
  }, [file, uploadStatus, checkSummaryStatus]);
  
  const handleDrop = (e) => {
    e.preventDefault();
    setIsFileDraggedOver(false);
    if (isUploadDisabled) return; // Check if upload is disabled

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const newFile = files[0]; // Assuming you're only interested in the first file
      setFile(newFile);
      setUploadStatus("selected"); // Set to 'selected' when a file is chosen
    }
  };
  
  const handleDragOver = (e) => {
    e.preventDefault(); 
    setIsFileDraggedOver(true); 
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsFileDraggedOver(false); // Set back to false when the file leaves the drag area
  };

  // Automatically try to upload after the file is selected
  React.useEffect(() => {
    if (uploadStatus === "selected") {
      handleUpload();
    }
  }, [uploadStatus, file, handleUpload]);

  // Update based on current state
  let buttonText = loggedIn ? 'Logout' : isConfirming ? 'Confirm' : 'Login/Signup';
  let buttonAction = loggedIn ? handleLogout : isConfirming ? handleConfirmCode : handleLoginSignup;

  return (
    <div className="App">
      <header className="App-header">
        <img src="/logo.png" alt="Logo" className="smaller-logo" />
        Summarise Your PDFs!
      </header>
      <p>Free trial summaries of five PDFs per person!</p>
      <p>Only the first two pages of any PDFs will be summarised during this trial.</p>
      <p>Three summaries will be provided for each page.</p>
      <p>Remember to save the summaries if you find them useful!</p>
      {/* Unified Login/Signup or Confirm button */}
      {!loggedIn && !isConfirming && <input type="text" value={userEmail} onChange={e => setUserEmail(e.target.value)} placeholder="User Email" />}
      {!loggedIn && !isConfirming && <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" />}
      {!loggedIn && isConfirming && <input type="password" value={confirmationCode} onChange={e => setConfirmationCode(e.target.value)} placeholder="6 Digits Confirmation Code" />}
      <button onClick={buttonAction}>{buttonText}</button>
      {isConfirming && <div>{confirmMessage}</div>}
      <div
        className={`file-upload-area ${isUploadDisabled ? 'disabled' : ''} ${isFileDraggedOver ? 'drag-over' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <div className="drag-drop-instructions" style={{ pointerEvents: 'none' }}>
          Drag and Drop your PDF file here.
        </div>
        <input
          type="file"
          style={{ display: 'none' }}
          ref={fileInputRef}
          onChange={handleFileSelect}
          accept=".pdf"
          disabled={isUploadDisabled}
        />
        <button onClick={handleButtonClick} disabled={uploadStatus !== "idle"}>
          Or click to upload your PDF file
        </button>
        {uploadStatus === "uploading" && <p>Uploading...</p>}
        {uploadStatus === "uploaded" && <p>File uploaded, summarizing...</p>} {/* New status message */}
        {uploadStatus === "completed" && <p>Summary complete!</p>}
        {uploadStatus === "error" && <p>Error during upload.</p>}
      </div>
      <div className="summary-area">
        Your PDF summarised.
        <textarea value={summary} readOnly={true} />
      </div>
    </div>
  );
}

export default App;
