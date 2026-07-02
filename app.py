import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime
import base64

# Page configuration
st.set_page_config(
    page_title="Advanced Floor Plan Maker",
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
    .element-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        border-left: 4px solid #1e3d59;
    }
    .legend-box {
        display: inline-block;
        width: 20px;
        height: 20px;
        margin-right: 8px;
        border: 1px solid #ccc;
        border-radius: 3px;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .download-btn {
        background: linear-gradient(90deg, #00b4db, #0083b0);
        color: white;
    }
    .clear-btn {
        background: linear-gradient(90deg, #f7971e, #ffd200);
        color: black;
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
if 'snap_to_grid' not in st.session_state:
    st.session_state.snap_to_grid = True
if 'grid_size' not in st.session_state:
    st.session_state.grid_size = 20
if 'selected_element' not in st.session_state:
    st.session_state.selected_element = None

# Element types with colors and icons
ELEMENT_TYPES = {
    "Wall": {"color": "#8B7355", "icon": "▬", "category": "Structure"},
    "Door": {"color": "#2E86AB", "icon": "🚪", "category": "Structure"},
    "Rack": {"color": "#D3A04A", "icon": "📦", "category": "Equipment"},
    "Cable Tray": {"color": "#6B8E23", "icon": "🪜", "category": "Cabling"},
    "Cable Route Blue": {"color": "#0066CC", "icon": "🔵", "category": "Cabling"},
    "Cable Route Green": {"color": "#00CC66", "icon": "🟢", "category": "Cabling"},
    "Cable Route Black": {"color": "#333333", "icon": "⚫", "category": "Cabling"},
    "Cable Route Yellow": {"color": "#FFCC00", "icon": "🟡", "category": "Cabling"},
    "Cable Route Red": {"color": "#CC0000", "icon": "🔴", "category": "Cabling"},
}

# Helper functions
def add_element(element_type, x, y, width, height, label, rotation=0):
    """Add a new element to the floor plan"""
    st.session_state.elements.append({
        'id': st.session_state.element_id,
        'type': element_type,
        'x': x,
        'y': y,
        'width': width,
        'height': height,
        'label': label,
        'rotation': rotation,
        'color': ELEMENT_TYPES[element_type]["color"],
        'icon': ELEMENT_TYPES[element_type]["icon"],
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    st.session_state.element_id += 1

def delete_element(element_id):
    """Delete an element by ID"""
    st.session_state.elements = [e for e in st.session_state.elements if e['id'] != element_id]

def clear_all_elements():
    """Clear all elements from the floor plan"""
    st.session_state.elements = []
    st.session_state.element_id = 0

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

def create_floor_plan_figure():
    """Create the floor plan visualization using Plotly"""
    fig = go.Figure()
    
    # Add grid if enabled
    if st.session_state.show_grid:
        grid_size = st.session_state.grid_size
        max_coord = 500
        
        # Grid lines
        for x in range(0, max_coord + grid_size, grid_size):
            fig.add_shape(
                type="line", x0=x, y0=0, x1=x, y1=max_coord,
                line=dict(color="rgba(200, 200, 200, 0.3)", width=0.5)
            )
        for y in range(0, max_coord + grid_size, grid_size):
            fig.add_shape(
                type="line", x0=0, y0=y, x1=max_coord, y1=y,
                line=dict(color="rgba(200, 200, 200, 0.3)", width=0.5)
            )
    
    # Add elements
    for elem in st.session_state.elements:
        x, y = elem['x'], elem['y']
        w, h = elem['width'], elem['height']
        color = elem['color']
        label = elem['label']
        elem_type = elem['type']
        rotation = elem.get('rotation', 0)
        
        # Determine shape type based on element
        if elem_type == "Wall":
            # Wall as a thick line
            fig.add_shape(
                type="rect", x0=x, y0=y, x1=x+w, y1=y+h,
                fillcolor=color, line=dict(color=color, width=2),
                opacity=0.8
            )
            # Add texture for walls
            fig.add_annotation(
                x=x+w/2, y=y+h/2,
                text="▬",
                font=dict(size=20, color="white"),
                showarrow=False,
                opacity=0.5
            )
        elif elem_type == "Door":
            # Door as an arc
            fig.add_shape(
                type="rect", x0=x, y0=y, x1=x+w, y1=y+h,
                fillcolor=color, line=dict(color=color, width=2),
                opacity=0.6
            )
            # Door arc
            fig.add_shape(
                type="path",
                path=f"M {x+w} {y} A {w} {h} 0 0 0 {x} {y+h}",
                line=dict(color=color, width=2)
            )
        elif elem_type == "Rack":
            # Rack as a box with shelves
            fig.add_shape(
                type="rect", x0=x, y0=y, x1=x+w, y1=y+h,
                fillcolor=color, line=dict(color="#8B6914", width=2),
                opacity=0.9
            )
            # Add shelf lines
            for i in range(1, 4):
                shelf_y = y + (h * i / 4)
                fig.add_shape(
                    type="line", x0=x+2, y0=shelf_y, x1=x+w-2, y1=shelf_y,
                    line=dict(color="#8B6914", width=1)
                )
        elif elem_type == "Cable Tray":
            # Cable tray as a ladder pattern
            fig.add_shape(
                type="rect", x0=x, y0=y, x1=x+w, y1=y+h,
                fillcolor=color, line=dict(color=color, width=2),
                opacity=0.7
            )
            # Ladder rungs
            for i in range(1, 6):
                rung_x = x + (w * i / 6)
                fig.add_shape(
                    type="line", x0=rung_x, y0=y+2, x1=rung_x, y1=y+h-2,
                    line=dict(color="white", width=1)
                )
        elif "Cable Route" in elem_type:
            # Cable routes as colored lines with arrows
            fig.add_shape(
                type="line", x0=x, y0=y, x1=x+w, y1=y+h,
                line=dict(color=color, width=6, dash="solid")
            )
            # Add arrowhead
            arrow_size = 10
            dx, dy = w, h
            length = np.sqrt(dx**2 + dy**2)
            if length > 0:
                ux, uy = dx/length, dy/length
                fig.add_shape(
                    type="path",
                    path=f"M {x+w} {y+h} L {x+w - arrow_size*ux + arrow_size*uy/2} {y+h - arrow_size*uy - arrow_size*ux/2} L {x+w - arrow_size*ux - arrow_size*uy/2} {y+h - arrow_size*uy + arrow_size*ux/2} Z",
                    fillcolor=color, line=dict(color=color, width=1)
                )
        
        # Add label for all elements
        if label:
            fig.add_annotation(
                x=x+w/2, y=y+h/2,
                text=f"{label}",
                font=dict(size=10, color="white", family="Arial Black"),
                showarrow=False,
                bgcolor="rgba(0,0,0,0.6)",
                borderpad=2,
                font_color="white"
            )
        
        # Add size indicator for larger elements
        if w > 20 or h > 20:
            fig.add_annotation(
                x=x+w/2, y=y-5,
                text=f"{w}x{h}",
                font=dict(size=8, color="#666"),
                showarrow=False
            )
    
    # Update layout
    fig.update_layout(
        width=900,
        height=700,
        xaxis=dict(
            range=[-10, 510],
            showgrid=False,
            zeroline=False,
            showticklabels=True,
            tickfont=dict(size=8)
        ),
        yaxis=dict(
            range=[-10, 510],
            showgrid=False,
            zeroline=False,
            showticklabels=True,
            tickfont=dict(size=8),
            scaleanchor="x",
            scaleratio=1
        ),
        plot_bgcolor='white',
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='closest',
        title=dict(
            text=f"📐 {st.session_state.floor_name}",
            font=dict(size=24, color="#1e3d59")
        )
    )
    
    return fig

# Main UI
st.markdown('<div class="main-header">🏗️ Advanced 2D Floor Plan Maker</div>', unsafe_allow_html=True)

# Sidebar - Controls
with st.sidebar:
    st.markdown("## 🎨 Design Tools")
    
    # Floor name
    st.session_state.floor_name = st.text_input("📋 Floor Name", st.session_state.floor_name)
    
    # Element creation
    st.markdown("### ➕ Add Element")
    col1, col2 = st.columns(2)
    with col1:
        element_type = st.selectbox("Type", list(ELEMENT_TYPES.keys()))
    with col2:
        rotation = st.number_input("Rotation (°)", 0, 360, 0, 15)
    
    col1, col2 = st.columns(2)
    with col1:
        width = st.number_input("Width", 20, 200, 40, 5)
    with col2:
        height = st.number_input("Height", 20, 200, 30, 5)
    
    col1, col2 = st.columns(2)
    with col1:
        x_pos = st.number_input("X Position", 0, 480, 50, 10)
    with col2:
        y_pos = st.number_input("Y Position", 0, 480, 50, 10)
    
    label = st.text_input("Label (optional)", "")
    
    if st.button("➕ Add Element", use_container_width=True):
        if st.session_state.snap_to_grid:
            grid = st.session_state.grid_size
            x_pos = round(x_pos / grid) * grid
            y_pos = round(y_pos / grid) * grid
            width = round(width / grid) * grid
            height = round(height / grid) * grid
        add_element(element_type, x_pos, y_pos, width, height, label, rotation)
        st.success(f"✅ Added {element_type}")
        st.rerun()
    
    st.markdown("---")
    
    # Element management
    st.markdown("### 🗂️ Element Management")
    if st.button("🗑️ Clear All", use_container_width=True, type="secondary"):
        clear_all_elements()
        st.rerun()
    
    # Grid settings
    st.markdown("### 📐 Grid Settings")
    st.session_state.show_grid = st.checkbox("Show Grid", st.session_state.show_grid)
    st.session_state.snap_to_grid = st.checkbox("Snap to Grid", st.session_state.snap_to_grid)
    st.session_state.grid_size = st.slider("Grid Size", 10, 50, 20, 5)
    
    # Export/Import
    st.markdown("### 💾 Export/Import")
    if st.button("📤 Export JSON", use_container_width=True):
        json_data = export_to_json()
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=f"{st.session_state.floor_name.replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    uploaded_file = st.file_uploader("📥 Import JSON", type=['json'])
    if uploaded_file is not None:
        try:
            json_data = uploaded_file.read().decode('utf-8')
            if import_from_json(json_data):
                st.success("✅ Import successful!")
                st.rerun()
        except:
            st.error("❌ Invalid JSON file")
    
    # Legend
    st.markdown("### 📖 Legend")
    for elem_type, info in ELEMENT_TYPES.items():
        st.markdown(
            f'<div style="display:flex; align-items:center; margin:2px 0;">'
            f'<span class="legend-box" style="background:{info["color"]};"></span>'
            f'<span style="font-size:0.9rem;">{info["icon"]} {elem_type}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

# Main content area
tab1, tab2, tab3 = st.tabs(["📐 Floor Plan", "📋 Element List", "📊 Statistics"])

with tab1:
    # Floor plan visualization
    fig = create_floor_plan_figure()
    st.plotly_chart(fig, use_container_width=True)
    
    # Quick info
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
        st.info("No elements added yet. Start designing your floor plan!")

with tab3:
    # Statistics and analytics
    st.markdown("### 📊 Floor Plan Analytics")
    
    if st.session_state.elements:
        col1, col2 = st.columns(2)
        
        with col1:
            # Element type distribution
            type_counts = pd.DataFrame(st.session_state.elements)['type'].value_counts()
            st.markdown("#### Element Type Distribution")
            st.bar_chart(type_counts)
        
        with col2:
            # Dimension statistics
            df = pd.DataFrame(st.session_state.elements)
            st.markdown("#### Dimension Statistics")
            st.write(f"**Total Area:** {df['width'].sum() * df['height'].sum():,.0f} sq units")
            st.write(f"**Average Width:** {df['width'].mean():.1f}")
            st.write(f"**Average Height:** {df['height'].mean():.1f}")
            st.write(f"**Largest Element:** {df.loc[df['width'].idxmax(), 'type']} ({df['width'].max()}x{df.loc[df['width'].idxmax(), 'height']})")
        
        # Cable route summary
        cable_routes = [e for e in st.session_state.elements if "Cable Route" in e['type']]
        if cable_routes:
            st.markdown("#### Cable Route Summary")
            cable_df = pd.DataFrame(cable_routes)
            cable_summary = cable_df.groupby('type').size().reset_index(name='count')
            st.dataframe(cable_summary, use_container_width=True)
    else:
        st.info("Add elements to see statistics")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        🏗️ Advanced Floor Plan Maker | Built with Streamlit & Plotly
    </div>
    """,
    unsafe_allow_html=True
)