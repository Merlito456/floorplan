import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime
import base64

# Page configuration
st.set_page_config(
    page_title="Advanced Floor Plan Maker - Drag & Drop",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for outstanding UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3d59;
        background: linear-gradient(90deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
    }
    .tool-btn {
        padding: 10px;
        margin: 5px;
        border-radius: 8px;
        border: 2px solid #ddd;
        background: white;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
        font-weight: 600;
    }
    .tool-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .tool-btn.active {
        border-color: #1e3d59;
        background: #e8f0fe;
    }
    .legend-box {
        display: inline-block;
        width: 20px;
        height: 20px;
        margin-right: 8px;
        border: 2px solid black;
        border-radius: 3px;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .canvas-container {
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 10px;
    }
    .instruction-banner {
        background: linear-gradient(90deg, #f0f4f8, #d9e2ec);
        padding: 0.8rem;
        border-radius: 8px;
        border-left: 4px solid #1e3d59;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'elements' not in st.session_state:
    st.session_state.elements = []
if 'element_id' not in st.session_state:
    st.session_state.element_id = 0
if 'floor_name' not in st.session_state:
    st.session_state.floor_name = "Floor Plan 1"
if 'show_grid' not in st.session_state:
    st.session_state.show_grid = True
if 'grid_size' not in st.session_state:
    st.session_state.grid_size = 20
if 'selected_tool' not in st.session_state:
    st.session_state.selected_tool = "Select"
if 'selected_element' not in st.session_state:
    st.session_state.selected_element = None
if 'canvas_data' not in st.session_state:
    st.session_state.canvas_data = None

# Element types with colors
ELEMENT_TYPES = {
    "Wall": {"color": "#8B7355", "bg_color": "#8B7355", "category": "Structure"},
    "Door": {"color": "#2E86AB", "bg_color": "#2E86AB", "category": "Structure"},
    "Rack": {"color": "#D3A04A", "bg_color": "#D3A04A", "category": "Equipment"},
    "Cable Tray": {"color": "#6B8E23", "bg_color": "#6B8E23", "category": "Cabling"},
    "Cable Route Blue": {"color": "#0066CC", "bg_color": "#0066CC", "category": "Cabling"},
    "Cable Route Green": {"color": "#00CC66", "bg_color": "#00CC66", "category": "Cabling"},
    "Cable Route Black": {"color": "#333333", "bg_color": "#333333", "category": "Cabling"},
    "Cable Route Yellow": {"color": "#FFCC00", "bg_color": "#FFCC00", "category": "Cabling"},
    "Cable Route Red": {"color": "#CC0000", "bg_color": "#CC0000", "category": "Cabling"},
}

# Helper functions
def add_element(element_type, x, y, width, height, label=""):
    """Add a new element to the floor plan"""
    st.session_state.elements.append({
        'id': st.session_state.element_id,
        'type': element_type,
        'x': x,
        'y': y,
        'width': width,
        'height': height,
        'label': label,
        'color': ELEMENT_TYPES[element_type]["color"],
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    st.session_state.element_id += 1

def delete_element(element_id):
    """Delete an element by ID"""
    st.session_state.elements = [e for e in st.session_state.elements if e['id'] != element_id]
    if st.session_state.selected_element == element_id:
        st.session_state.selected_element = None

def clear_all_elements():
    """Clear all elements from the floor plan"""
    st.session_state.elements = []
    st.session_state.element_id = 0
    st.session_state.selected_element = None

def export_to_json():
    """Export floor plan data to JSON"""
    data = {
        'floor_name': st.session_state.floor_name,
        'elements': st.session_state.elements,
        'grid_size': st.session_state.grid_size,
        'export_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return json.dumps(data, indent=2)

def import_from_json(json_data):
    """Import floor plan data from JSON"""
    try:
        data = json.loads(json_data)
        st.session_state.floor_name = data.get('floor_name', 'Imported Plan')
        st.session_state.elements = data.get('elements', [])
        st.session_state.grid_size = data.get('grid_size', 20)
        if st.session_state.elements:
            st.session_state.element_id = max([e['id'] for e in st.session_state.elements]) + 1
        return True
    except:
        return False

def get_elements_json():
    """Get elements as JSON string for JavaScript"""
    return json.dumps(st.session_state.elements)

# Main UI
st.markdown('<div class="main-header">🏗️ Advanced Floor Plan Maker - Drag & Drop</div>', unsafe_allow_html=True)

# Sidebar - Controls
with st.sidebar:
    st.markdown("## 🎨 Tools")
    
    # Tool selection
    tools = ["Select", "Draw", "Move", "Delete"]
    tool_icons = ["👆", "✏️", "✋", "🗑️"]
    
    for tool, icon in zip(tools, tool_icons):
        is_active = st.session_state.selected_tool == tool
        if st.button(
            f"{icon} {tool}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state.selected_tool = tool
            st.rerun()
    
    st.markdown("---")
    
    # Element type selection for drawing
    st.markdown("### 📐 Element Type")
    element_type = st.selectbox(
        "Select type to draw",
        list(ELEMENT_TYPES.keys()),
        key="draw_type"
    )
    
    # Show element info
    info = ELEMENT_TYPES[element_type]
    st.info(f"📌 {info['category']}")
    
    st.markdown("---")
    
    # Properties
    st.markdown("### 🏷️ Properties")
    draw_label = st.text_input("Label", "", key="draw_label")
    
    col1, col2 = st.columns(2)
    with col1:
        default_width = st.number_input("Width", 20, 200, 40, 5, key="draw_width")
    with col2:
        default_height = st.number_input("Height", 20, 200, 30, 5, key="draw_height")
    
    st.markdown("---")
    
    # Grid settings
    st.markdown("### 📐 Grid Settings")
    st.session_state.show_grid = st.checkbox("Show Grid", st.session_state.show_grid)
    st.session_state.grid_size = st.slider("Grid Size", 10, 50, 20, 5)
    
    st.markdown("---")
    
    # Export/Import
    st.markdown("### 💾 Export/Import")
    
    if st.button("📤 Export JSON", use_container_width=True):
        json_data = export_to_json()
        st.download_button(
            label="📥 Download",
            data=json_data,
            file_name=f"{st.session_state.floor_name.replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    if st.button("🗑️ Clear All", use_container_width=True, type="secondary"):
        clear_all_elements()
        st.rerun()
    
    uploaded_file = st.file_uploader("📥 Import JSON", type=['json'])
    if uploaded_file is not None:
        try:
            json_data = uploaded_file.read().decode('utf-8')
            if import_from_json(json_data):
                st.success("✅ Import successful!")
                st.rerun()
        except:
            st.error("❌ Invalid JSON file")
    
    st.markdown("---")
    
    # Legend
    st.markdown("### 📖 Legend")
    for elem_type, info in ELEMENT_TYPES.items():
        st.markdown(
            f'<div style="display:flex; align-items:center; margin:2px 0;">'
            f'<span class="legend-box" style="background:{info["color"]};"></span>'
            f'<span style="font-size:0.9rem;">{elem_type}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    st.metric("Total Elements", len(st.session_state.elements))

# Main content
tab1, tab2, tab3 = st.tabs(["📐 Floor Plan", "📋 Element List", "📊 Statistics"])

with tab1:
    st.markdown("""
    <div class="instruction-banner">
        🎯 <b>Instructions:</b> 
        Select a tool from the sidebar → Click and drag on the canvas to draw or move elements
    </div>
    """, unsafe_allow_html=True)
    
    # Canvas container
    st.markdown('<div class="canvas-container">', unsafe_allow_html=True)
    
    # Create HTML with JavaScript canvas
    elements_json = get_elements_json()
    selected_tool = st.session_state.selected_tool
    element_type = st.session_state.get('draw_type', 'Wall')
    draw_label = st.session_state.get('draw_label', '')
    draw_width = st.session_state.get('draw_width', 40)
    draw_height = st.session_state.get('draw_height', 30)
    show_grid = st.session_state.show_grid
    grid_size = st.session_state.grid_size
    selected_element = st.session_state.selected_element
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ margin: 0; padding: 0; background: white; }}
            #canvas {{
                display: block;
                width: 100%;
                height: 700px;
                cursor: crosshair;
                border: 2px solid #ddd;
                border-radius: 8px;
                background: white;
            }}
            #tooltip {{
                position: absolute;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                pointer-events: none;
                display: none;
            }}
            .element-label {{
                font-size: 11px;
                font-weight: bold;
                color: white;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
                pointer-events: none;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <canvas id="canvas"></canvas>
        <div id="tooltip"></div>
        
        <script>
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');
            
            // Set canvas size
            function resizeCanvas() {{
                const rect = canvas.parentElement.getBoundingClientRect();
                canvas.width = rect.width - 4;
                canvas.height = 700;
            }}
            resizeCanvas();
            window.addEventListener('resize', resizeCanvas);
            
            // State
            let elements = {elements_json};
            let selectedTool = '{selected_tool}';
            let elementType = '{element_type}';
            let drawLabel = '{draw_label}';
            let drawWidth = {draw_width};
            let drawHeight = {draw_height};
            let showGrid = {str(show_grid).lower()};
            let gridSize = {grid_size};
            let selectedElementId = {selected_element if selected_element is not None else 'null'};
            
            // Drawing state
            let isDrawing = false;
            let startX = 0;
            let startY = 0;
            let currentX = 0;
            let currentY = 0;
            let isDragging = false;
            let dragElementId = null;
            let dragOffsetX = 0;
            let dragOffsetY = 0;
            let hoveredElement = null;
            
            // Element colors
            const elementColors = {json.dumps({k: v["color"] for k, v in ELEMENT_TYPES.items()})};
            
            // Get element color
            function getElementColor(type) {{
                return elementColors[type] || '#888';
            }}
            
            // Snap to grid
            function snapToGrid(value) {{
                return Math.round(value / gridSize) * gridSize;
            }}
            
            // Draw grid
            function drawGrid() {{
                if (!showGrid) return;
                ctx.strokeStyle = 'rgba(200, 200, 200, 0.3)';
                ctx.lineWidth = 0.5;
                
                for (let x = 0; x <= canvas.width; x += gridSize) {{
                    ctx.beginPath();
                    ctx.moveTo(x, 0);
                    ctx.lineTo(x, canvas.height);
                    ctx.stroke();
                }}
                
                for (let y = 0; y <= canvas.height; y += gridSize) {{
                    ctx.beginPath();
                    ctx.moveTo(0, y);
                    ctx.lineTo(canvas.width, y);
                    ctx.stroke();
                }}
            }}
            
            // Draw an element
            function drawElement(elem) {{
                const x = elem.x;
                const y = elem.y;
                const w = elem.width;
                const h = elem.height;
                const color = elem.color;
                const type = elem.type;
                const label = elem.label || '';
                const isSelected = (selectedElementId === elem.id);
                
                ctx.save();
                
                // Draw shape based on type
                ctx.shadowColor = 'rgba(0,0,0,0.1)';
                ctx.shadowBlur = 4;
                ctx.shadowOffsetX = 2;
                ctx.shadowOffsetY = 2;
                
                if (type === 'Wall') {{
                    ctx.fillStyle = color;
                    ctx.fillRect(x, y, w, h);
                    ctx.shadowBlur = 0;
                    ctx.strokeStyle = isSelected ? 'red' : 'black';
                    ctx.lineWidth = isSelected ? 3 : 2;
                    ctx.strokeRect(x, y, w, h);
                    ctx.fillStyle = 'rgba(255,255,255,0.3)';
                    ctx.font = '20px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText('▬', x + w/2, y + h/2);
                }} else if (type === 'Door') {{
                    ctx.fillStyle = color;
                    ctx.fillRect(x, y, w, h);
                    ctx.shadowBlur = 0;
                    ctx.strokeStyle = isSelected ? 'red' : 'black';
                    ctx.lineWidth = isSelected ? 3 : 2;
                    ctx.strokeRect(x, y, w, h);
                    ctx.beginPath();
                    ctx.arc(x + w, y, w, -Math.PI/2, 0);
                    ctx.strokeStyle = isSelected ? 'red' : 'black';
                    ctx.lineWidth = isSelected ? 3 : 2;
                    ctx.stroke();
                }} else if (type === 'Rack') {{
                    ctx.fillStyle = color;
                    ctx.fillRect(x, y, w, h);
                    ctx.shadowBlur = 0;
                    ctx.strokeStyle = isSelected ? 'red' : 'black';
                    ctx.lineWidth = isSelected ? 3 : 2;
                    ctx.strokeRect(x, y, w, h);
                    // Shelves
                    ctx.strokeStyle = 'black';
                    ctx.lineWidth = 1.5;
                    for (let i = 1; i < 4; i++) {{
                        const shelfY = y + (h * i / 4);
                        ctx.beginPath();
                        ctx.moveTo(x + 2, shelfY);
                        ctx.lineTo(x + w - 2, shelfY);
                        ctx.stroke();
                    }}
                    // Vertical line
                    ctx.setLineDash([4, 4]);
                    ctx.beginPath();
                    ctx.moveTo(x + w/2, y);
                    ctx.lineTo(x + w/2, y + h);
                    ctx.stroke();
                    ctx.setLineDash([]);
                }} else if (type === 'Cable Tray') {{
                    ctx.fillStyle = color;
                    ctx.fillRect(x, y, w, h);
                    ctx.shadowBlur = 0;
                    ctx.strokeStyle = isSelected ? 'red' : 'black';
                    ctx.lineWidth = isSelected ? 3 : 2;
                    ctx.strokeRect(x, y, w, h);
                    // Ladder rungs
                    ctx.strokeStyle = 'black';
                    ctx.lineWidth = 1.5;
                    for (let i = 1; i < 6; i++) {{
                        const rungX = x + (w * i / 6);
                        ctx.beginPath();
                        ctx.moveTo(rungX, y + 2);
                        ctx.lineTo(rungX, y + h - 2);
                        ctx.stroke();
                    }}
                    // Side rails
                    ctx.beginPath();
                    ctx.moveTo(x, y + 2);
                    ctx.lineTo(x + w, y + 2);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(x, y + h - 2);
                    ctx.lineTo(x + w, y + h - 2);
                    ctx.stroke();
                }} else if (type.includes('Cable Route')) {{
                    // Cable route with arrow
                    ctx.shadowBlur = 0;
                    ctx.strokeStyle = 'black';
                    ctx.lineWidth = 8;
                    ctx.beginPath();
                    ctx.moveTo(x, y);
                    ctx.lineTo(x + w, y + h);
                    ctx.stroke();
                    
                    ctx.strokeStyle = color;
                    ctx.lineWidth = 5;
                    ctx.beginPath();
                    ctx.moveTo(x, y);
                    ctx.lineTo(x + w, y + h);
                    ctx.stroke();
                    
                    // Arrow
                    const angle = Math.atan2(h, w);
                    const arrowSize = 12;
                    const endX = x + w;
                    const endY = y + h;
                    
                    ctx.fillStyle = 'black';
                    ctx.beginPath();
                    ctx.moveTo(endX, endY);
                    ctx.lineTo(endX - arrowSize * Math.cos(angle - 0.5), endY - arrowSize * Math.sin(angle - 0.5));
                    ctx.lineTo(endX - arrowSize * Math.cos(angle + 0.5), endY - arrowSize * Math.sin(angle + 0.5));
                    ctx.closePath();
                    ctx.fill();
                    
                    ctx.fillStyle = color;
                    ctx.beginPath();
                    ctx.moveTo(endX - 2, endY - 2);
                    ctx.lineTo(endX - (arrowSize-3) * Math.cos(angle - 0.5), endY - (arrowSize-3) * Math.sin(angle - 0.5));
                    ctx.lineTo(endX - (arrowSize-3) * Math.cos(angle + 0.5), endY - (arrowSize-3) * Math.sin(angle + 0.5));
                    ctx.closePath();
                    ctx.fill();
                }}
                
                // Draw label
                if (label) {{
                    ctx.shadowBlur = 0;
                    ctx.fillStyle = 'rgba(0,0,0,0.7)';
                    const labelX = x + w/2;
                    const labelY = y + h/2;
                    ctx.font = 'bold 10px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    const metrics = ctx.measureText(label);
                    const padding = 4;
                    const rectWidth = metrics.width + padding * 2;
                    const rectHeight = 20;
                    ctx.fillRect(labelX - rectWidth/2, labelY - rectHeight/2, rectWidth, rectHeight);
                    ctx.fillStyle = 'white';
                    ctx.fillText(label, labelX, labelY);
                }}
                
                // Draw size indicator
                if (w > 20 || h > 20) {{
                    ctx.shadowBlur = 0;
                    ctx.fillStyle = 'rgba(255,255,255,0.8)';
                    const sizeText = `${w}×${h}`;
                    ctx.font = '9px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'bottom';
                    const metrics = ctx.measureText(sizeText);
                    const padding = 2;
                    const rectWidth = metrics.width + padding * 2;
                    const rectHeight = 14;
                    ctx.fillRect(x + w/2 - rectWidth/2, y - rectHeight - 2, rectWidth, rectHeight);
                    ctx.strokeStyle = 'black';
                    ctx.lineWidth = 0.5;
                    ctx.strokeRect(x + w/2 - rectWidth/2, y - rectHeight - 2, rectWidth, rectHeight);
                    ctx.fillStyle = '#333';
                    ctx.textBaseline = 'bottom';
                    ctx.fillText(sizeText, x + w/2, y - 2);
                }}
                
                ctx.restore();
            }}
            
            // Main draw function
            function draw() {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // Draw grid
                drawGrid();
                
                // Draw all elements
                elements.forEach(elem => {{
                    drawElement(elem);
                }});
                
                // Draw preview for drawing
                if (isDrawing) {{
                    ctx.save();
                    ctx.strokeStyle = 'red';
                    ctx.lineWidth = 2;
                    ctx.setLineDash([5, 5]);
                    const x = Math.min(startX, currentX);
                    const y = Math.min(startY, currentY);
                    const w = Math.abs(currentX - startX);
                    const h = Math.abs(currentY - startY);
                    ctx.strokeRect(x, y, w, h);
                    ctx.fillStyle = getElementColor(elementType);
                    ctx.globalAlpha = 0.3;
                    ctx.fillRect(x, y, w, h);
                    ctx.restore();
                }}
            }}
            
            // Mouse events for drawing and dragging
            canvas.addEventListener('mousedown', function(e) {{
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;
                const x = (e.clientX - rect.left) * scaleX;
                const y = (e.clientY - rect.top) * scaleY;
                
                if (selectedTool === 'Draw') {{
                    isDrawing = true;
                    startX = x;
                    startY = y;
                    currentX = x;
                    currentY = y;
                }} else if (selectedTool === 'Select' || selectedTool === 'Move') {{
                    // Check if clicked on an element
                    for (let i = elements.length - 1; i >= 0; i--) {{
                        const elem = elements[i];
                        if (x >= elem.x && x <= elem.x + elem.width &&
                            y >= elem.y && y <= elem.y + elem.height) {{
                            selectedElementId = elem.id;
                            if (selectedTool === 'Move') {{
                                isDragging = true;
                                dragElementId = elem.id;
                                dragOffsetX = x - elem.x;
                                dragOffsetY = y - elem.y;
                            }}
                            // Send selection to Python
                            window.parent.postMessage({{
                                type: 'select_element',
                                id: elem.id
                            }}, '*');
                            draw();
                            return;
                        }}
                    }}
                    // Click on empty space
                    selectedElementId = null;
                    window.parent.postMessage({{
                        type: 'select_element',
                        id: null
                    }}, '*');
                    draw();
                }} else if (selectedTool === 'Delete') {{
                    // Check if clicked on an element
                    for (let i = elements.length - 1; i >= 0; i--) {{
                        const elem = elements[i];
                        if (x >= elem.x && x <= elem.x + elem.width &&
                            y >= elem.y && y <= elem.y + elem.height) {{
                            // Send delete request to Python
                            window.parent.postMessage({{
                                type: 'delete_element',
                                id: elem.id
                            }}, '*');
                            return;
                        }}
                    }}
                }}
            }});
            
            canvas.addEventListener('mousemove', function(e) {{
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;
                const x = (e.clientX - rect.left) * scaleX;
                const y = (e.clientY - rect.top) * scaleY;
                
                if (isDrawing) {{
                    currentX = x;
                    currentY = y;
                    draw();
                }} else if (isDragging && dragElementId !== null) {{
                    const elem = elements.find(e => e.id === dragElementId);
                    if (elem) {{
                        let newX = snapToGrid(x - dragOffsetX);
                        let newY = snapToGrid(y - dragOffsetY);
                        newX = Math.max(0, Math.min(newX, canvas.width - elem.width));
                        newY = Math.max(0, Math.min(newY, canvas.height - elem.height));
                        elem.x = newX;
                        elem.y = newY;
                        // Send update to Python
                        window.parent.postMessage({{
                            type: 'move_element',
                            id: elem.id,
                            x: newX,
                            y: newY
                        }}, '*');
                        draw();
                    }}
                }}
            }});
            
            canvas.addEventListener('mouseup', function(e) {{
                if (isDrawing) {{
                    const rect = canvas.getBoundingClientRect();
                    const scaleX = canvas.width / rect.width;
                    const scaleY = canvas.height / rect.height;
                    const x = (e.clientX - rect.left) * scaleX;
                    const y = (e.clientY - rect.top) * scaleY;
                    
                    const x1 = snapToGrid(Math.min(startX, x));
                    const y1 = snapToGrid(Math.min(startY, y));
                    const w = snapToGrid(Math.abs(x - startX));
                    const h = snapToGrid(Math.abs(y - startY));
                    
                    if (w > 5 && h > 5) {{
                        // Send new element to Python
                        window.parent.postMessage({{
                            type: 'add_element',
                            elementType: elementType,
                            x: x1,
                            y: y1,
                            width: w,
                            height: h,
                            label: drawLabel
                        }}, '*');
                    }}
                    
                    isDrawing = false;
                    draw();
                }}
                
                if (isDragging) {{
                    isDragging = false;
                    dragElementId = null;
                }}
            }});
            
            canvas.addEventListener('mouseleave', function() {{
                if (isDrawing) {{
                    isDrawing = false;
                    draw();
                }}
                if (isDragging) {{
                    isDragging = false;
                    dragElementId = null;
                }}
            }});
            
            // Listen for messages from Python
            window.addEventListener('message', function(event) {{
                if (event.data.type === 'update_elements') {{
                    elements = event.data.elements;
                    selectedElementId = event.data.selectedElement;
                    draw();
                }}
            }});
            
            // Initial draw
            draw();
            
            // Handle canvas resize
            window.addEventListener('resize', function() {{
                resizeCanvas();
                draw();
            }});
        </script>
    </body>
    </html>
    """
    
    # Display the HTML canvas
    st.components.v1.html(html_code, height=720, scrolling=False)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Elements", len(st.session_state.elements))
    with col2:
        walls = len([e for e in st.session_state.elements if e['type'] == "Wall"])
        st.metric("Walls", walls)
    with col3:
        racks = len([e for e in st.session_state.elements if e['type'] == "Rack"])
        st.metric("Racks", racks)
    with col4:
        cables = len([e for e in st.session_state.elements if "Cable Route" in e['type']])
        st.metric("Cable Routes", cables)

with tab2:
    # Element list with management
    if st.session_state.elements:
        df = pd.DataFrame(st.session_state.elements)
        display_df = df[['id', 'type', 'label', 'x', 'y', 'width', 'height', 'timestamp']]
        display_df.columns = ['ID', 'Type', 'Label', 'X', 'Y', 'Width', 'Height', 'Created']
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # Delete specific element
        col1, col2 = st.columns([3, 1])
        with col1:
            delete_id = st.number_input("Enter ID to delete", min_value=0, step=1)
        with col2:
            if st.button("🗑️ Delete", use_container_width=True):
                if delete_id in df['id'].values:
                    delete_element(delete_id)
                    st.success(f"✅ Deleted element {delete_id}")
                    st.rerun()
                else:
                    st.error("❌ ID not found")
    else:
        st.info("No elements added yet. Use the Draw tool to add elements!")

with tab3:
    # Statistics
    st.markdown("### 📊 Floor Plan Analytics")
    
    if st.session_state.elements:
        col1, col2 = st.columns(2)
        
        with col1:
            type_counts = pd.DataFrame(st.session_state.elements)['type'].value_counts()
            st.markdown("#### Element Type Distribution")
            st.bar_chart(type_counts)
        
        with col2:
            df = pd.DataFrame(st.session_state.elements)
            st.markdown("#### Dimension Statistics")
            st.write(f"**Total Area:** {df['width'].sum() * df['height'].sum():,.0f} sq units")
            st.write(f"**Average Width:** {df['width'].mean():.1f}")
            st.write(f"**Average Height:** {df['height'].mean():.1f}")
            if len(df) > 0:
                st.write(f"**Largest Element:** {df.loc[df['width'].idxmax(), 'type']} ({df['width'].max()}×{df.loc[df['width'].idxmax(), 'height']})")
    else:
        st.info("Add elements to see statistics")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        🏗️ Advanced Floor Plan Maker | Click & Drag to Draw | Drag to Move | Select & Delete
    </div>
    """,
    unsafe_allow_html=True
)