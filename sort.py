import streamlit as st
from graphviz import Digraph
import random
import time

# --- Animated Heap Class ---
class AnimatedHeap:
    def __init__(self, is_min=True):
        self.heap = []
        self.is_min = is_min

    def _compare(self, a, b):
        return a < b if self.is_min else a > b

    def swap_and_visualize(self, i, j, st_plot):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        st_plot.graphviz_chart(draw_heap_tree(self.heap, highlight_nodes=[i, j]))
        time.sleep(1)

    def _heapify_up(self, index, st_plot):
        while index > 0:
            parent = (index - 1) // 2
            if self._compare(self.heap[index], self.heap[parent]):
                self.swap_and_visualize(index, parent, st_plot)
                index = parent
            else:
                break

    def _heapify_down(self, index, st_plot):
        size = len(self.heap)
        while True:
            swap_idx = index
            left = 2 * index + 1
            right = 2 * index + 2

            if left < size and self._compare(self.heap[left], self.heap[swap_idx]):
                swap_idx = left
            if right < size and self._compare(self.heap[right], self.heap[swap_idx]):
                swap_idx = right

            if swap_idx != index:
                self.swap_and_visualize(index, swap_idx, st_plot)
                index = swap_idx
            else:
                break

    def build_heap(self, arr, st_plot):
        self.heap = arr[:]
        st_plot.graphviz_chart(draw_heap_tree(self.heap))
        time.sleep(1)
        for i in reversed(range(len(self.heap)//2)):
            self._heapify_down(i, st_plot)

    def insert(self, val, st_plot):
        self.heap.append(val)
        self._heapify_up(len(self.heap) - 1, st_plot)

    def delete_root(self, st_plot):
        if not self.heap:
            st.warning("Heap is empty!")
            return None
        root = self.heap[0]
        last = self.heap.pop()
        if self.heap:
            self.heap[0] = last
            self._heapify_down(0, st_plot)
        return root

    def get_heap(self):
        return self.heap

# --- Visualization with UNIFORM circle sizes and HIGHLIGHTING ---
def draw_heap_tree(heap, highlight_nodes=None):
    dot = Digraph()
    dot.attr(bgcolor="black")
    highlight_nodes = highlight_nodes or []
    
    for i, val in enumerate(heap):
        # HIGHLIGHT nodes being swapped in RED
        if i in highlight_nodes:
            node_color = "#FF4B4B"
            font_color = "white"
        else:
            node_color = "white"
            font_color = "black"
        
        # UNIFORM CIRCLE SIZE
        dot.node(
            str(i), str(val),
            shape="circle",
            style="filled",
            color=node_color,
            fontcolor=font_color,
            fixedsize="true",
            width="0.8",
            height="0.8",
            fontsize="14"
        )
        
        left, right = 2 * i + 1, 2 * i + 2
        if left < len(heap):
            dot.edge(str(i), str(left), color='green')
        if right < len(heap):
            dot.edge(str(i), str(right), color='green')
    return dot

# --- SINGLE PAGE STREAMLIT APP ---
st.set_page_config(page_title="Heap Visualizer", layout="wide")
st.title(" Interactive Heap Visualizer")

# Initialize session state
if "animated_heap" not in st.session_state:
    st.session_state.animated_heap = None
if "vis_placeholder" not in st.session_state:
    st.session_state.vis_placeholder = None

# === HEAP SETUP SECTION ===
st.header("1. Setup Heap")
col1, col2 = st.columns(2)

with col1:
    heap_type = st.radio("Heap Type", ["Min Heap", "Max Heap"])

with col2:
    input_mode = st.radio("Input Mode", ["Manual Entry", "Random List"])

# Input handling
if input_mode == "Manual Entry":
    values = st.text_input("Enter numbers (comma separated)", value="10, 20, 15, 30, 40,1,6,55,90,87")
    try:
        input_list = [int(x.strip()) for x in values.split(",") if x.strip()]
        # DISPLAY AS SIMPLE LIST
        st.write("**Input List:**", str(input_list))
    except ValueError:
        st.error("Please enter only integers separated by commas.")
        input_list = []
else:
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        size = st.number_input("List size", min_value=1, max_value=30, value=12)
    with col_b:
        min_val = st.number_input("Min value", value=1)
    with col_c:
        max_val = st.number_input("Max value", value=100)
    
    input_list = [random.randint(int(min_val), int(max_val)) for _ in range(int(size))]
    
    # DISPLAY RANDOM LIST AS SIMPLE LIST FORMAT
    st.write("**Generated Random List:**", str(input_list))

# Build heap button
if st.button(" Animate Heapify"):
    is_min = heap_type == "Min Heap"
    st.session_state.animated_heap = AnimatedHeap(is_min=is_min)
    
    # Create visualization placeholder ONCE
    st.session_state.vis_placeholder = st.empty()
    
    # Build and animate heap
    st.session_state.animated_heap.build_heap(input_list, st.session_state.vis_placeholder)
    st.success("Heap built successfully! Use the buttons below to interact with the heap.")

# === VISUALIZATION & OPERATIONS SECTION ===
if st.session_state.animated_heap is not None:
    st.header("2. Heap Visualization")
    
    # Show current heap if no placeholder exists
    if st.session_state.vis_placeholder is None:
        st.session_state.vis_placeholder = st.empty()
    
    # Always show current heap state
    st.session_state.vis_placeholder.graphviz_chart(
        draw_heap_tree(st.session_state.animated_heap.get_heap())
    )
    
    st.header("3. Interactive Operations")
    
    # INSERT AND DELETE BUTTONS - ANIMATE ON SAME TREE WITH HIGHLIGHTING
    col1, col2, col3 = st.columns(3)
    
    with col1:
        insert_val = st.number_input("Value to insert", value=50)
        if st.button("📥 Insert Node"):
            # Use the SAME placeholder for animation WITH HIGHLIGHTING
            st.session_state.animated_heap.insert(insert_val, st.session_state.vis_placeholder)
            st.success(f"✅ Inserted {insert_val}")
            # Show final state without highlighting
            st.session_state.vis_placeholder.graphviz_chart(
                draw_heap_tree(st.session_state.animated_heap.get_heap())
            )
    
    with col2:
        st.write('')
        if st.button("🗑️ Delete Root"):
            # Use the SAME placeholder for animation WITH HIGHLIGHTING
            deleted = st.session_state.animated_heap.delete_root(st.session_state.vis_placeholder)
            if deleted is not None:
                st.success(f"✅ Deleted root: {deleted}")
                # Show final state without highlighting
                st.session_state.vis_placeholder.graphviz_chart(
                    draw_heap_tree(st.session_state.animated_heap.get_heap())
                )
    
    with col3:
        st.metric("Heap Size", len(st.session_state.animated_heap.get_heap()))
    
    # CURRENT HEAP ARRAY AS SIMPLE LIST
    st.subheader("Current Heap Array:")
    current_heap = st.session_state.animated_heap.get_heap()
    if current_heap:
        st.write(str(current_heap))  # Simple list format like [10, 45, 34]
    else:
        st.write("[]")  # Empty list

else:
    st.info("👆 Please build a heap first to see visualization and operations.")
