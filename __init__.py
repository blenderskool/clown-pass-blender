bl_info = {
    "name": "Clown Pass",
    "author": "Akash Hamirwasia",
    "version": (1, 0),
    "blender": (2, 75, 0),
    "location": "Properties > Render Layers",
    "description": "A Clown Pass Creator",
    "warning": "",
    "wiki_url": "http://www.blenderskool.cf",
    "tracker_url": "",
    "category": "Node"}

import bpy
import random
mat_count = 0
enable_clown = False

""" A Popup window that warns the user that the add-on shall modify the Material ID of all the
    Materials. It would be user's choice to accept it or decline it """
class ClownNotice(bpy.types.Operator):
    bl_idname = "clown.notice"
    bl_label = "Modify Material IDs?"
    bl_description = "Install Clown"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.separator()
        col.label("Add-on relies on Material IDs to work.")
        col.separator()
        col.label("Do you want the add-on to modify the Material IDs")
        col.label("for all the materials in the scene?")
        col.separator()
        col.separator()

    def execute(self,context):
        global enable_clown
        enable_clown = True
        run_clown(self)
        return {'FINISHED'}

def run_clown(self):
    """ Core engine of the add-on. This function generates the node group with all the nodes to setup
    the clown mask. Node Setup uses the Material ID pass of the Render Layer and uses it with
    the IDMask node to separate each material. Each material is then given a separate color using
    MixRGB node. Several such combinations of each material are combined to produce the final clown
    mask map """
    i=1
    global mat_count
    for mat in bpy.data.materials:
        mat.pass_index = i
        i=i+1
        mat_count = mat_count+1

    bpy.context.scene.render.layers.active.use_pass_material_index = True

    """ The above code changes the Material Index value for all the materials in the scene and prepares the scene for Clown Mask node setup generation in RunClown Operator """

    bpy.context.scene.use_nodes = True
    prev_mix = None
    group = None
    y_loc = 433.178  # Starting Location of the Node Generation. It is modified throughout the generation process
    x_loc = -250.344

    try:  # If a Clown Mask node group already exists then modify it without creating a new group
        group = bpy.data.node_groups['Clown Mask']
        for node in group.nodes:
            group.nodes.remove(node)
        group_inputs = group.nodes.new('NodeGroupInput')
        group_inputs.location = -928.319, 85.763
        group_outputs = group.nodes.new('NodeGroupOutput')

    except: # If node group does not exist, create a new one
        group = bpy.data.node_groups.new('Clown Mask', 'CompositorNodeTree')
        group.inputs.new('NodeSocketColor', 'IndexMA')
        group.outputs.new('NodeSocketColor', 'Mask')
        group_inputs = group.nodes.new('NodeGroupInput')
        group_inputs.location = -928.319, 85.763
        group_outputs = group.nodes.new('NodeGroupOutput')

    # Node Setup creation Process
    for i in range(1, len(bpy.data.materials)+1):
        node_tree = group
        id_mask = node_tree.nodes.new("CompositorNodeIDMask")  # Adds an ID Mask node
        id_mask.location = -468.344, y_loc
        mix = node_tree.nodes.new("CompositorNodeMixRGB")      # Adds a MixRGB node
        mix.location = x_loc, y_loc
        node_tree.links.new(id_mask.inputs[0], group_inputs.outputs['IndexMA'])  # Links the Id Mask node with the group input of Material Index Pass

        if i == 1:  # if it is the first node, then connect it to the id_mask itself
            node_tree.links.new(mix.inputs[1], id_mask.outputs[0])
        else: # Connect the new Mix node to the Previous Mix node
            node_tree.links.new(mix.inputs[1], prev_mix.outputs[0])

        node_tree.links.new(mix.inputs[0], id_mask.outputs[0])

        id_mask.index = i    # Setting the Material Index to separate the material from the scene
        #prev_id = id_mask
        prev_mix = mix
        mix.inputs[2].default_value = random.random(), random.random(), random.random(), 1.0  # Setup the random color of the MixRGB node that separates it from other materials
        y_loc = y_loc - 200  # Modifying the location of the nodes for the next loop run
        x_loc = x_loc + 200

    # Loop Ends

    # The final Mask is for the World matetrial. This would separate the world from of the scene with a separate color given to it.
    world_mask = node_tree.nodes.new('CompositorNodeIDMask')
    world_mask.location = -468.344, y_loc
    world_mix = node_tree.nodes.new('CompositorNodeMixRGB')
    world_mix.location = x_loc, y_loc
    world_mask.index = 0
    group_outputs.location = x_loc+200,y_loc

    # Connected with the rest of the setup
    node_tree.links.new(world_mask.inputs[0], group_inputs.outputs['IndexMA'])
    node_tree.links.new(world_mix.inputs[0], world_mask.outputs[0])
    node_tree.links.new(world_mix.inputs[1], prev_mix.outputs[0])
    node_tree.links.new(world_mix.outputs[0], group_outputs.inputs['Mask'])
    world_mix.inputs[2].default_value = random.random(), random.random(), random.random(), 1.0  # Random color is given to the world Mask


""" Main add-on interface located in the Render Layers panel in the Properties Window """
def passes_panel(self, context):
    layout = self.layout

    col = layout.column(align=True)
    layer = bpy.context.scene.clown_mask
    col.prop(layer, 'use_pass_clown', text='Clown Mask')

""" All the Clown Mask add-on properties. Can be accessed through bpy.context.scene.clown_mask """
class ClownProps(bpy.types.PropertyGroup):
    def set_clown(self, context):
        global enable_clown
        clown_mask = bpy.context.scene.clown_mask
        if enable_clown == False and clown_mask.use_pass_clown == True:
            enable_clown = True
            bpy.ops.clown.notice('INVOKE_DEFAULT')
        else:
            if clown_mask.use_pass_clown == False:
                enable_clown = True

        if clown_mask.use_pass_clown == True:
                run_clown(self)
        return None

    """ Main Checkbox Boolean that allows the user to enable/disable the Clown Mask pass """
    use_pass_clown = bpy.props.BoolProperty(name="Clown", description="Enable Clown Mask", update=set_clown)


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.clown_mask = bpy.props.PointerProperty(type=ClownProps)
    bpy.types.CyclesRender_PT_layer_passes.append(passes_panel)  # Appends the add-on panel to the Render Layers Panel
    bpy.app.handlers.render_post.append(run_clown)  # App Handler that invokes run_clown() just after a render is finished rendering to setup the clown mask

def unregister():
    global enable_clown
    enable_clown = False # Resetting some values just after the add-on is deactivated

    del bpy.types.Scene.clown_mask
    bpy.utils.unregister_module(__name__)
    bpy.types.CyclesRender_PT_layer_passes.remove(passes_panel) # Removes the add-on panel from the Render Layers Panel
    bpy.app.handlers.render_post.remove(run_clown)  # Removes the App Handler
