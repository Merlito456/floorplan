import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime
import random

# Page configuration
st.set_page_config(
    page_title="Interactive Floor Plan Maker",
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
    .tool-card {
        background: white;
        padding: 0.8rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.3rem 0;
        cursor: pointer;
        transition: all 0.3s;
        border: 2px solid transparent;
        text-align: center;
    }
    .tool-card:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .tool-card.active {
        border-color: #1e3d59;
        background: #e8f0fe;
    }
    .tool-card .icon {
        font-size: 1.5rem;
    }
    .tool-card .label {
        font-size: 0.9rem;
        font-weight: 600;
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
    .legend-box {
        display: inline-block;
        width: 20px;
        height: 20px;
        margin-right: 8px;
        border: 2px solid black;
        border-radius: 3px;
    }
    .instruction-banner {
        background: linear-gradient(90deg, #f0f4f8, #d9e2ec);
        padding: 0.8rem;
        border-radius: 8px;
        border-left: 4px solid #1e3d59;
        margin: 0.5rem 0;
    }
    .placement-indicator {
        background: rgba(30, 61, 89, 0.1);
        border: 2px dashed #1e3d59;
        border-radius: 4px;
        padding: 0.5rem;
        text-align: center;
        font-weight: 600;
        color: #1e3d59;
    }
    .element-preview {
        border: 2px solid #1e3d59;
        border-radius: 4px;
        padding: 0.5rem;
        background: white;
        margin: 0.2rem 0;
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
if 'mode' not in st.session_state:
    st.session_state.mode = "view"  # "view", "place", "move", "delete"
if 'placement_mode' not in st.session_state:
    st.session_state.placement_mode = False
if 'drag_element' not in st.session_state:
    st.session_state.drag_element = None
if 'mouse_x' not in st.session_state:
    st.session_state.mouse_x = 50
if 'mouse_y' not in st.session_state:
    st.session_state.mouse_y = 50

# Element types with colors and icons
ELEMENT_TYPES = {
    "Wall": {"color": "#8B7355", "icon": "▬", "category": "Structure", "draw_type": "rectangle"},
    "Door": {"color": "#2E86AB", "icon": "🚪", "category": "Structure", "draw_type": "rectangle"},
    "Rack": {"color": "#D3A04A", "icon": "📦", "category": "Equipment", "draw_type": "rectangle"},
    "Cable Tray": {"color": "#6B8E23", "icon": "🪜", "category": "Cabling", "draw_type": "rectangle"},
    "Cable Route Blue": {"color": "#0066CC", "icon": "🔵", "category": "Cabling", "draw_type": "line"},
    "Cable Route Green": {"color": "#00CC66", "icon": "🟢", "category": "Cabling", "draw_type": "line"},
    "Cable Route Black": {"color": "#333333", "icon": "⚫", "category": "Cabling", "draw_type": "line"},
    "Cable Route Yellow": {"color": "#FFCC00", "icon": "🟡", "category": "Cabling", "draw_type": "line"},
    "Cable Route Red": {"color": "#CC0000", "icon": "🔴", "category": "Cabling", "draw_type": "line"},
}

# Helper functions
def add_element(element_type, x, y, width, height, label="", rotation=0):
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

def snap_to_grid(value):
    """Snap value to grid"""
    grid = st.session_state.grid_size
    return round(value / grid) * grid

def create_floor_plan_figure():
    """Create the floor plan visualization using Plotly"""
    fig = go.Figure()
    
    canvas_size = 500
    
    # Add grid if enabled
    if st.session_state.show_grid:
        grid_size = st.session_state.grid_size
        for x in range(0, canvas_size + grid_size, grid_size):
            fig.add_shape(
                type="line", x0=x, y0=0, x1=x, y1=canvas_size,
                line=dict(color="rgba(200, 200, 200, 0.3)", width=0.5),
                layer="below"
            )
        for y in range(0, canvas_size + grid_size, grid_size):
            fig.add_shape(
                type="line", x0=0, y0=y, x1=canvas_size, y1=y,
                line=dict(color="rgba(200, 200, 200, 0.3)", width=0.5),
                layer="below"
            )
    
    # Add elements
    for elem in st.session_state.elements:
        x, y = elem['x'], elem['y']
        w, h = elem['width'], elem['height']
        color = elem['color']
        label = elem['label']
        elem_type = elem['type']
        is_selected = (st.session_state.selected_element == elem['id'])
        
        border_color = "red" if is_selected else "black"
        border_width = 3 if is_selected else 2
        
        if elem_type == "Wall":
            fig.add_shape(
                type="rect", x0=x, y0=y, x1=x+w, y1=y+h,
                fillcolor=color, 
                line=dict(color=border_color, width=border_width),
                opacity=0.8,
                layer="above"
            )
            fig.add_annotation(
                x=x+w/2, y=y+h/2,
                text="▬",
                font=dict(size=20, color="white"),
                showarrow=False,
                opacity=0.5
            )
        elif elem_type == "Door":
            fig.add_shape(
                type="rect", x0=x, y0=y, x1=x+w, y1=y+h,
                fillcolor=color, 
                line=dict(color=border_color, width=border_width),
                opacity=0.6,
                layer="above"
            )
            fig.add_shape(
                type="path",
                path=f"M {x+w} {y} A {w} {h} 0 0 0 {x} {y+h}",
                line=dict(color=border_color, width=border_width),
                layer="above"
            )
        elif elem_type == "Rack":
            fig.add_shape(
                type="rect", x0=x, y0=y, x1=x+w, y1=y+h,
                fillcolor=color, 
                line=dict(color=border_color, width=border_width),
                opacity=0.9,
                layer="above"
            )
            for i in range(1, 4):
                shelf_y = y + (h * i / 4)
                fig.add_shape(
                    type="line", x0=x+2, y0=shelf_y, x1=x+w-2, y1=shelf_y,
                    line=dict(color="black", width=1.5),
                    layer="above"
                )
            fig.add_shape(
                type="line", x0=x+w/2, y0=y, x1=x+w/2, y1=y+h,
                line=dict(color="black", width=1, dash="dot"),
                layer="above"
            )
        elif elem_type == "Cable Tray":
            fig.add_shape(
                type="rect", x0=x, y0=y, x1=x+w, y1=y+h,
                fillcolor=color, 
                line=dict(color=border_color, width=border_width),
                opacity=0.7,
                layer="above"
            )
            for i in range(1, 6):
                rung_x = x + (w * i / 6)
                fig.add_shape(
                    type="line", x0=rung_x, y0=y+2, x1=rung_x, y1=y+h-2,
                    line=dict(color="black", width=1.5),
                    layer="above"
                )
            fig.add_shape(
                type="line", x0=x, y0=y+2, x1=x+w, y1=y+2,
                line=dict(color="black", width=1.5),
                layer="above"
            )
            fig.add_shape(
                type="line", x0=x, y0=y+h-2, x1=x+w, y1=y+h-2,
                line=dict(color="black", width=1.5),
                layer="above"
            )
        elif "Cable Route" in elem_type:
            fig.add_shape(
                type="line", x0=x, y0=y, x1=x+w, y1=y+h,
                line=dict(color="black", width=8, dash="solid"),
                layer="above"
            )
            fig.add_shape(
                type="line", x0=x, y0=y, x1=x+w, y1=y+h,
                line=dict(color=color, width=5, dash="solid"),
                layer="above"
            )
            arrow_size = 12
            dx, dy = w, h
            length = np.sqrt(dx**2 + dy**2)
            if length > 0:
                ux, uy = dx/length, dy/length
                fig.add_shape(
                    type="path",
                    path=f"M {x+w} {y+h} L {x+w - arrow_size*ux + arrow_size*uy/2} {y+h - arrow_size*uy - arrow_size*ux/2} L {x+w - arrow_size*ux - arrow_size*uy/2} {y+h - arrow_size*uy + arrow_size*ux/2} Z",
                    fillcolor="black", 
                    line=dict(color="black", width=1),
                    layer="above"
                )
                fig.add_shape(
                    type="path",
                    path=f"M {x+w-2} {y+h-2} L {x+w - (arrow_size-3)*ux + (arrow_size-3)*uy/2} {y+h - (arrow_size-3)*uy - (arrow_size-3)*ux/2} L {x+w - (arrow_size-3)*ux - (arrow_size-3)*uy/2} {y+h - (arrow_size-3)*uy + (arrow_size-3)*ux/2} Z",
                    fillcolor=color, 
                    line=dict(color="black", width=0.5),
                    layer="above"
                )
        
        if label:
            fig.add_annotation(
                x=x+w/2, y=y+h/2,
                text=f"{label}",
                font=dict(size=10, color="white", family="Arial Black"),
                showarrow=False,
                bgcolor="rgba(0,0,0,0.7)",
                borderpad=3,
                font_color="white",
                border_color="black",
                border_width=1
            )
        
        if w > 20 or h > 20:
            fig.add_annotation(
                x=x+w/2, y=y-8,
                text=f"{w}×{h}",
                font=dict(size=9, color="#333", family="Arial"),
                showarrow=False,
                bgcolor="rgba(255,255,255,0.8)",
                borderpad=2,
                border_color="black",
                border_width=0.5
            )
    
    # Add placement preview if in placement mode
    if st.session_state.placement_mode:
        x = st.session_state.mouse_x
        y = st.session_state.mouse_y
        w = st.session_state.get('preview_width', 40)
        h = st.session_state.get('preview_height', 30)
        elem_type = st.session_state.get('preview_type', 'Wall')
        color = ELEMENT_TYPES[elem_type]["color"]
        
        fig.add_shape(
            type="rect", x0=x, y0=y, x1=x+w, y1=y+h,
            fillcolor=color,
            line=dict(color="red", width=2, dash="dash"),
            opacity=0.5,
            layer="above"
        )
        fig.add_annotation(
            x=x+w/2, y=y-15,
            text="📍 Click to place",
            font=dict(size=10, color="red"),
            showarrow=True,
            arrowhead=1,
            arrowcolor="red"
        )
    
    fig.update_layout(
        width=900,
        height=700,
        xaxis=dict(
            range=[-10, 510],
            showgrid=False,
            zeroline=False,
            showticklabels=True,
            tickfont=dict(size=8),
            fixedrange=False
        ),
        yaxis=dict(
            range=[-10, 510],
            showgrid=False,
            zeroline=False,
            showticklabels=True,
            tickfont=dict(size=8),
            scaleanchor="x",
            scaleratio=1,
            fixedrange=False
        ),
        plot_bgcolor='white',
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='closest',
        dragmode='pan',
        title=dict(
            text=f"📐 {st.session_state.floor_name}",
            font=dict(size=24, color="#1e3d59")
        ),
        clickmode='event+select'
    )
    
    return fig

# Main UI
st.markdown('<div class="main-header">🏗️ Interactive Floor Plan Maker</div>', unsafe_allow_html=True)

# Instruction banner
mode_instructions = {
    "Select": "🖱️ Click on elements to select them. Selected elements show a red border.",
    "Place": "✏️ Click anywhere on the canvas to place the selected element type.",
    "Move": "✋ Click on an element to select it, then use the slider below to move it.",
    "Delete": "🗑️ Click on an element to delete it."
}

current_instruction = mode_instructions.get(st.session_state.selected_tool, "Select a tool to begin")
st.markdown(f"""
<div class="instruction-banner">
    {current_instruction}
</div>
""", unsafe_allow_html=True)

# Sidebar - Controls
with st.sidebar:
    st.markdown("## 🎨 Tools")
    
    # Tool selection with better UI
    tools = ["Select", "Place", "Move", "Delete"]
    tool_icons = ["👆", "✏️", "✋", "🗑️"]
    tool_descriptions = ["Click to select", "Click to place", "Click & drag", "Click to delete"]
    
    for tool, icon, desc in zip(tools, tool_icons, tool_descriptions):
        is_active = st.session_state.selected_tool == tool
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"<div style='font-size:1.5rem;'>{icon}</div>", unsafe_allow_html=True)
        with col2:
            if st.button(
                f"{tool}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.selected_tool = tool
                if tool == "Place":
                    st.session_state.placement_mode = True
                else:
                    st.session_state.placement_mode = False
                st.rerun()
            st.caption(desc)
    
    st.markdown("---")
    
    # Element type selection (only visible in Place mode)
    if st.session_state.selected_tool == "Place":
        st.markdown("### 📐 Element Type")
        
        # Grid of element types
        cols = st.columns(2)
        for idx, (elem_type, info) in enumerate(ELEMENT_TYPES.items()):
            with cols[idx % 2]:
                is_selected = st.session_state.get('preview_type') == elem_type
                if st.button(
                    f"{info['icon']} {elem_type[:12]}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary"
                ):
                    st.session_state.preview_type = elem_type
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### 📏 Size Controls")
        
        # Size controls for placement
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.preview_width = st.slider(
                "Width",
                10, 100, 40, 5,
                key="place_width"
            )
        with col2:
            st.session_state.preview_height = st.slider(
                "Height",
                10, 100, 30, 5,
                key="place_height"
            )
        
        # Label input
        st.session_state.place_label = st.text_input("Label (optional)", "")
        
        # Position preview
        st.markdown("### 📍 Position")
        st.markdown(f"X: {st.session_state.mouse_x}, Y: {st.session_state.mouse_y}")
        
        # Place button
        if st.button("📍 Place at Current Position", use_container_width=True, type="primary"):
            elem_type = st.session_state.get('preview_type', 'Wall')
            label = st.session_state.get('place_label', '')
            x = snap_to_grid(st.session_state.mouse_x)
            y = snap_to_grid(st.session_state.mouse_y)
            w = snap_to_grid(st.session_state.preview_width)
            h = snap_to_grid(st.session_state.preview_height)
            add_element(elem_type, x, y, w, h, label)
            st.success(f"✅ Added {elem_type}")
            st.rerun()
    
    st.markdown("---")
    
    # Grid settings
    st.markdown("### 📐 Grid Settings")
    st.session_state.show_grid = st.checkbox("Show Grid", st.session_state.show_grid)
    st.session_state.grid_size = st.slider("Grid Size", 10, 50, 20, 5)
    
    # Move controls (visible in Move mode)
    if st.session_state.selected_tool == "Move" and st.session_state.selected_element is not None:
        st.markdown("---")
        st.markdown("### 🔄 Move Selected Element")
        
        # Find the selected element
        selected = None
        for elem in st.session_state.elements:
            if elem['id'] == st.session_state.selected_element:
                selected = elem
                break
        
        if selected:
            st.markdown(f"**{selected['type']}** - ID: {selected['id']}")
            
            col1, col2 = st.columns(2)
            with col1:
                new_x = st.slider(
                    "X Position",
                    0, 460, selected['x'], 10,
                    key="move_x"
                )
            with col2:
                new_y = st.slider(
                    "Y Position",
                    0, 460, selected['y'], 10,
                    key="move_y"
                )
            
            if st.button("🔄 Update Position", use_container_width=True):
                # Update element position
                for elem in st.session_state.elements:
                    if elem['id'] == st.session_state.selected_element:
                        elem['x'] = snap_to_grid(new_x)
                        elem['y'] = snap_to_grid(new_y)
                        st.success("✅ Position updated!")
                        st.rerun()
                        break
    
    st.markdown("---")
    
    # Export/Import
    st.markdown("### 💾 Export/Import")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📤 Export", use_container_width=True):
            json_data = export_to_json()
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"{st.session_state.floor_name.replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col2:
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
            f'<span style="font-size:0.9rem;">{info["icon"]} {elem_type}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    # Element count
    st.markdown("---")
    st.metric("Total Elements", len(st.session_state.elements))

# Main content area
tab1, tab2, tab3 = st.tabs(["📐 Floor Plan", "📋 Element List", "📊 Statistics"])

with tab1:
    # Create and display the floor plan
    fig = create_floor_plan_figure()
    
    # Display the plot
    config = {
        'displayModeBar': True,
        'modeBarButtonsToAdd': ['drawrect', 'drawline', 'eraseshape'],
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'displaylogo': False,
        'scrollZoom': True,
        'doubleClick': 'reset'
    }
    
    # Use plotly with click events
    event = st.plotly_chart(fig, use_container_width=True, config=config, key="floor_plan")
    
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
        
        # Quick actions
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            delete_id = st.number_input("Enter ID to delete or select", min_value=0, step=1)
        with col2:
            if st.button("🗑️ Delete", use_container_width=True):
                if delete_id in df['id'].values:
                    delete_element(delete_id)
                    st.success(f"✅ Deleted element {delete_id}")
                    st.rerun()
                else:
                    st.error("❌ ID not found")
        with col3:
            if st.button("🎯 Select", use_container_width=True):
                if delete_id in df['id'].values:
                    st.session_state.selected_element = delete_id
                    st.session_state.selected_tool = "Select"
                    st.success(f"✅ Selected element {delete_id}")
                    st.rerun()
                else:
                    st.error("❌ ID not found")
    else:
        st.info("No elements added yet. Use the Place tool to add elements!")

with tab3:
    # Statistics and analytics
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
        🏗️ Interactive Floor Plan Maker | Select a tool to start designing
    </div>
    """,
    unsafe_allow_html=True
)