import { useEffect, useRef, useState } from "react";
import { Camera, CameraOff, ImagePlus, RotateCcw } from "lucide-react";

export default function VisionCapture({ onImageChange }) {
  const videoRef = useRef(null);
  const [stream, setStream] = useState(null);
  const [preview, setPreview] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (videoRef.current && stream) videoRef.current.srcObject = stream;
    return () => {
      if (stream) stream.getTracks().forEach(track => track.stop());
    };
  }, [stream]);

  useEffect(() => () => { if (preview) URL.revokeObjectURL(preview); }, [preview]);

  async function startCamera() {
    setError("");
    try {
      if (!navigator.mediaDevices?.getUserMedia) throw new Error("Camera access requires HTTPS or localhost and a supported browser.");
      const media = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false });
      setStream(media);
    } catch (err) {
      setError(err.message || "Unable to access the camera. Check browser permissions.");
    }
  }

  function stopCamera() {
    if (stream) stream.getTracks().forEach(track => track.stop());
    setStream(null);
  }

  function setSelected(file) {
    if (!file) return;
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      setError("Choose a JPEG, PNG or WebP image.");
      return;
    }
    if (preview) URL.revokeObjectURL(preview);
    setPreview(URL.createObjectURL(file));
    onImageChange(file);
    setError("");
  }

  function capture() {
    const video = videoRef.current;
    if (!video?.videoWidth) {
      setError("The camera is not ready yet.");
      return;
    }
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    canvas.toBlob(blob => {
      if (!blob) {
        setError("Unable to capture the image.");
        return;
      }
      setSelected(new File([blob], "support-issue.jpg", { type: "image/jpeg" }));
      stopCamera();
    }, "image/jpeg", 0.9);
  }

  function clearImage() {
    if (preview) URL.revokeObjectURL(preview);
    setPreview("");
    onImageChange(null);
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <div className="flex items-center gap-2 font-semibold"><Camera size={18} className="text-indigo-600" />Attach a photo of the issue <span className="text-xs font-normal text-slate-500">(optional)</span></div>
      <p className="mt-1 text-xs text-slate-500">Mirage will describe visible evidence. The support agents will use that description alongside your ticket.</p>
      {stream && <div className="mt-3 space-y-2"><video ref={videoRef} autoPlay playsInline className="max-h-72 w-full rounded-lg bg-black object-contain" /><div className="flex gap-2"><button type="button" onClick={capture} className="rounded-lg bg-indigo-600 px-3 py-2 text-sm font-semibold text-white">Capture photo</button><button type="button" onClick={stopCamera} className="rounded-lg border bg-white px-3 py-2 text-sm"><CameraOff size={15} className="inline mr-1" />Stop camera</button></div></div>}
      {!stream && <div className="mt-3 flex flex-wrap gap-2"><button type="button" onClick={startCamera} className="rounded-lg bg-indigo-600 px-3 py-2 text-sm font-semibold text-white"><Camera size={15} className="mr-1 inline" />Use camera</button><label className="cursor-pointer rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"><ImagePlus size={15} className="mr-1 inline" />Upload image<input type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={e => setSelected(e.target.files?.[0])} /></label></div>}
      {preview && <div className="mt-3 flex flex-wrap items-start gap-3"><img src={preview} alt="Selected issue" className="max-h-36 rounded-lg border object-contain" /><button type="button" onClick={clearImage} className="flex items-center gap-1 rounded-lg border bg-white px-3 py-2 text-sm"><RotateCcw size={14} />Remove image</button></div>}
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </div>
  );
}
