'use client';

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';

interface Point {
  x: number;
  y: number;
}

interface Stroke {
  id: string;
  points: Point[];
  color: string;
  width: number;
  timestamp: number;
}

interface DrawingEvent {
  type: 'start' | 'draw' | 'end';
  strokeId: string;
  point?: Point;
  color?: string;
  width?: number;
}

const Whiteboard: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const socketRef = useRef<Socket | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [currentColor, setCurrentColor] = useState('#000000');
  const [brushWidth, setBrushWidth] = useState(2);
  const [strokes, setStrokes] = useState<Map<string, Stroke>>(new Map());
  const [currentStroke, setCurrentStroke] = useState<Stroke | null>(null);

  // Initialize socket connection
  useEffect(() => {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    console.log('Whiteboard connecting to backend URL:', backendUrl);
    
    socketRef.current = io(backendUrl, {
      transports: ['websocket', 'polling']
    });

    const socket = socketRef.current;

    // Listen for drawing events from other users
    socket.on('drawing', (data: DrawingEvent) => {
      handleRemoteDrawing(data);
    });

    // Listen for clear events
    socket.on('clear', () => {
      clearCanvas();
    });

    socket.on('connect_error', (error) => {
      console.error('Whiteboard socket connection error:', error);
    });

    socket.on('error', (error) => {
      console.error('Whiteboard socket error:', error);
    });

    // Cleanup on unmount
    return () => {
      socket.disconnect();
    };
  }, []);

  // Handle remote drawing events
  const handleRemoteDrawing = useCallback((data: DrawingEvent) => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    switch (data.type) {
      case 'start':
        if (data.color && data.width) {
          const newStroke: Stroke = {
            id: data.strokeId,
            points: data.point ? [data.point] : [],
            color: data.color,
            width: data.width,
            timestamp: Date.now()
          };
          setStrokes(prev => new Map(prev.set(data.strokeId, newStroke)));
        }
        break;

      case 'draw':
        if (data.point) {
          setStrokes(prev => {
            const updated = new Map(prev);
            const stroke = updated.get(data.strokeId);
            if (stroke) {
              const updatedStroke = {
                ...stroke,
                points: [...stroke.points, data.point!]
              };
              updated.set(data.strokeId, updatedStroke);
            }
            return updated;
          });
        }
        break;

      case 'end':
        // Stroke is complete, no additional action needed
        break;
    }
  }, []);

  // Redraw canvas when strokes change
  useEffect(() => {
    if (!canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Redraw all strokes
    strokes.forEach(stroke => {
      if (stroke.points.length < 2) return;

      ctx.beginPath();
      ctx.strokeStyle = stroke.color;
      ctx.lineWidth = stroke.width;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';

      ctx.moveTo(stroke.points[0].x, stroke.points[0].y);
      for (let i = 1; i < stroke.points.length; i++) {
        ctx.lineTo(stroke.points[i].x, stroke.points[i].y);
      }
      ctx.stroke();
    });
  }, [strokes]);

  // Get mouse/touch position relative to canvas
  const getPointFromEvent = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>): Point => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    let clientX: number, clientY: number;

    if ('touches' in e) {
      // Touch event
      clientX = e.touches[0].clientX;
      clientY = e.touches[0].clientY;
    } else {
      // Mouse event
      clientX = e.clientX;
      clientY = e.clientY;
    }

    return {
      x: (clientX - rect.left) * scaleX,
      y: (clientY - rect.top) * scaleY
    };
  };

  // Start drawing
  const startDrawing = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    console.log('Start drawing');
    const point = getPointFromEvent(e);
    const strokeId = `stroke_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const newStroke: Stroke = {
      id: strokeId,
      points: [point],
      color: currentColor,
      width: brushWidth,
      timestamp: Date.now()
    };

    setCurrentStroke(newStroke);
    setIsDrawing(true);

    // Emit start event
    if (socketRef.current) {
      console.log('Emitting drawing start event');
      socketRef.current.emit('drawing', {
        type: 'start',
        strokeId,
        point,
        color: currentColor,
        width: brushWidth
      } as DrawingEvent);
    }
  };

  // Draw
  const draw = (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
    if (!isDrawing || !currentStroke) return;
    
    e.preventDefault();
    const point = getPointFromEvent(e);

    setCurrentStroke(prev => prev ? { ...prev, points: [...prev.points, point] } : null);

    // Emit draw event
    if (socketRef.current) {
      socketRef.current.emit('drawing', {
        type: 'draw',
        strokeId: currentStroke.id,
        point
      } as DrawingEvent);
    }
  };

  // Stop drawing
  const stopDrawing = () => {
    if (!isDrawing || !currentStroke) return;

    setIsDrawing(false);
    setStrokes(prev => new Map(prev.set(currentStroke.id, currentStroke)));
    setCurrentStroke(null);

    // Emit end event
    if (socketRef.current) {
      socketRef.current.emit('drawing', {
        type: 'end',
        strokeId: currentStroke.id
      } as DrawingEvent);
    }
  };

  // Clear canvas
  const clearCanvas = () => {
    setStrokes(new Map());
    setCurrentStroke(null);
    
    if (canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    }

    // Emit clear event
    if (socketRef.current) {
      socketRef.current.emit('clear');
    }
  };

  // Set up canvas size
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const resizeCanvas = () => {
      const container = canvas.parentElement;
      if (container) {
        const rect = container.getBoundingClientRect();
        canvas.width = rect.width;
        canvas.height = rect.height;
        
        // Set canvas display size to match container
        canvas.style.width = rect.width + 'px';
        canvas.style.height = rect.height + 'px';
        
        console.log('Canvas resized to:', rect.width, 'x', rect.height);
      }
    };

    // Initial resize
    resizeCanvas();
    
    // Resize on window resize
    window.addEventListener('resize', resizeCanvas);
    
    // Resize when component mounts
    const timeoutId = setTimeout(resizeCanvas, 100);

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      clearTimeout(timeoutId);
    };
  }, []);

  return (
    <div className="flex flex-col h-full bg-gray-100">
      {/* Toolbar */}
      <div className="flex items-center gap-4 p-4 bg-white border-b border-gray-200">
        {/* Color Picker */}
        <div className="flex items-center gap-2">
          <label htmlFor="color-picker" className="text-sm font-medium text-gray-700">
            Color:
          </label>
          <input
            id="color-picker"
            type="color"
            value={currentColor}
            onChange={(e) => setCurrentColor(e.target.value)}
            className="w-8 h-8 border border-gray-300 rounded cursor-pointer"
          />
        </div>

        {/* Brush Width */}
        <div className="flex items-center gap-2">
          <label htmlFor="brush-width" className="text-sm font-medium text-gray-700">
            Width:
          </label>
          <input
            id="brush-width"
            type="range"
            min="1"
            max="20"
            value={brushWidth}
            onChange={(e) => setBrushWidth(Number(e.target.value))}
            className="w-20"
          />
          <span className="text-sm text-gray-600 w-6">{brushWidth}</span>
        </div>

        {/* Clear Button */}
        <button
          onClick={clearCanvas}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
        >
          Clear
        </button>

        {/* Connection Status */}
        <div className="ml-auto flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${socketRef.current?.connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-sm text-gray-600">
            {socketRef.current?.connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Canvas */}
      <div className="flex-1 relative overflow-hidden bg-white border border-gray-200" style={{ minHeight: '400px' }}>
        <canvas
          ref={canvasRef}
          className="absolute inset-0 cursor-crosshair w-full h-full"
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseLeave={stopDrawing}
          onTouchStart={startDrawing}
          onTouchMove={draw}
          onTouchEnd={stopDrawing}
          style={{ touchAction: 'none' }}
        />
      </div>
    </div>
  );
};

export default Whiteboard;
