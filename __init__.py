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
class ClownSetup(bpy.types.Operator):
    bl_idname="clown.setup"
    bl_label="Setup"

    def execute(self, context):
        i=1
        global mat_count
        for mat in bpy.data.materials:
            mat.pass_index = i
            i=i+1
            mat_count = mat_count+1
        return{'FINISHED'}

class RunClown(bpy.types.Operator):
    bl_idname='clown.run'
    bl_label='Run'

    def execute(self, context):
        bpy.context.scene.use_nodes = True
        global mat_count
        prev_mix = None
        group = None
        y_loc = 433.178
        x_loc = -250.344
        try:
            group = bpy.data.node_groups['Clown Mask']
            for node in group.nodes:
                group.nodes.remove(node)
            group_inputs = group.nodes.new('NodeGroupInput')
            group_inputs.location = -928.319, 85.763
            group_outputs = group.nodes.new('NodeGroupOutput')
        except:
            group = bpy.data.node_groups.new('Clown Mask', 'CompositorNodeTree')
            group.inputs.new('NodeSocketColor', 'IndexMA')
            group.outputs.new('NodeSocketColor', 'Mask')
            group_inputs = group.nodes.new('NodeGroupInput')
            group_inputs.location = -928.319, 85.763
            group_outputs = group.nodes.new('NodeGroupOutput')

        for i in range(1, len(bpy.data.materials)+1):
            node_tree = group
            layer = group_inputs
            id_mask = node_tree.nodes.new("CompositorNodeIDMask")
            id_mask.location = -468.344, y_loc
            mix = node_tree.nodes.new("CompositorNodeMixRGB")
            mix.location = x_loc, y_loc
            node_tree.links.new(id_mask.inputs[0], layer.outputs['IndexMA'])
            if i == 1:
                node_tree.links.new(mix.inputs[1], id_mask.outputs[0])
            else:
                node_tree.links.new(mix.inputs[1], prev_mix.outputs[0])
            node_tree.links.new(mix.inputs[0], id_mask.outputs[0])
            id_mask.index = i
            #prev_id = id_mask
            prev_mix = mix
            mix.inputs[2].default_value = random.random(), random.random(), random.random(), 1.0
            y_loc = y_loc - 200
            x_loc = x_loc + 200
        world_mask = node_tree.nodes.new('CompositorNodeIDMask')
        world_mask.location = -468.344, y_loc
        world_mix = node_tree.nodes.new('CompositorNodeMixRGB')
        world_mix.location = x_loc, y_loc
        world_mask.index = 0
        group_outputs.location = x_loc+200,y_loc
        node_tree.links.new(world_mask.inputs[0], layer.outputs['IndexMA'])
        node_tree.links.new(world_mix.inputs[0], world_mask.outputs[0])
        node_tree.links.new(world_mix.inputs[1], prev_mix.outputs[0])
        node_tree.links.new(world_mix.outputs[0], group_outputs.inputs['Mask'])
        world_mix.inputs[2].default_value = random.random(), random.random(), random.random(), 1.0

        return{'FINISHED'}

class clown_notice(bpy.types.Operator):
    bl_idname = "clown.notice"
    bl_label = "Clown Notice"
    bl_description = "Install Clown"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.separator()
        row = col.row(align=True)
        row.label("Replace ID's")
        col.separator()

    def execute(self,context):
        global enable_clown
        enable_clown = True
        bpy.context.scene.clown_mask.clown_bool_mask = True
        return {'FINISHED'}

def PassesPanel(self, context):
    layout = self.layout

    col = layout.column(align=True)
    layer = bpy.context.scene.clown_mask#.render.layers.active.clown_mask
    col.prop(layer, 'clown_bool_mask', text='Clown Mask')
    col.operator(clown_notice.bl_idname)
    #col.operator(ClownSetup.bl_idname, text="Setup")
    #col.operator(RunClown.bl_idname, text="Run")

class ClownProps(bpy.types.PropertyGroup):
    def set_clown(self, context):
        render_layer = bpy.context.scene.clown_mask
        global enable_clown
        if enable_clown == False:
            enable_clown = True
            render_layer.clown_bool_mask = False
            bpy.ops.clown.notice('INVOKE_DEFAULT')
        else:
            if render_layer.clown_bool_mask == True:
                bpy.ops.clown.setup('INVOKE_DEFAULT')
                bpy.ops.clown.run('INVOKE_DEFAULT')
        return None

    clown_bool_mask = bpy.props.BoolProperty(name="Clown", description="Enable Clown Mask", update=set_clown)

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.clown_mask = bpy.props.PointerProperty(type=ClownProps)
    bpy.types.CyclesRender_PT_layer_passes.append(PassesPanel)
    bpy.app.handlers.render_post.append(run_clown)

def unregister():
    del bpy.types.Scene.clown_mask
    global enable_clown
    enable_clown = False
    bpy.utils.unregister_module(__name__)
    bpy.types.CyclesRender_PT_layer_passes.remove(PassesPanel)
    bpy.app.handlers.render_post.clear(run_clown)

def run_clown(self):
    i=1
    global mat_count
    for mat in bpy.data.materials:
        mat.pass_index = i
        i=i+1
        mat_count = mat_count+1

    bpy.context.scene.use_nodes = True
    global mat_count
    prev_mix = None
    group = None
    y_loc = 433.178
    x_loc = -250.344
    try:
        group = bpy.data.node_groups['Clown Mask']
        for node in group.nodes:
            group.nodes.remove(node)
        group_inputs = group.nodes.new('NodeGroupInput')
        group_inputs.location = -928.319, 85.763
        group_outputs = group.nodes.new('NodeGroupOutput')
    except:
        group = bpy.data.node_groups.new('Clown Mask', 'CompositorNodeTree')
        group.inputs.new('NodeSocketColor', 'IndexMA')
        group.outputs.new('NodeSocketColor', 'Mask')
        group_inputs = group.nodes.new('NodeGroupInput')
        group_inputs.location = -928.319, 85.763
        group_outputs = group.nodes.new('NodeGroupOutput')

    for i in range(1, len(bpy.data.materials)+1):
        node_tree = group
        layer = group_inputs
        id_mask = node_tree.nodes.new("CompositorNodeIDMask")
        id_mask.location = -468.344, y_loc
        mix = node_tree.nodes.new("CompositorNodeMixRGB")
        mix.location = x_loc, y_loc
        node_tree.links.new(id_mask.inputs[0], layer.outputs['IndexMA'])
        if i == 1:
            node_tree.links.new(mix.inputs[1], id_mask.outputs[0])
        else:
            node_tree.links.new(mix.inputs[1], prev_mix.outputs[0])
        node_tree.links.new(mix.inputs[0], id_mask.outputs[0])
        id_mask.index = i
        #prev_id = id_mask
        prev_mix = mix
        mix.inputs[2].default_value = random.random(), random.random(), random.random(), 1.0
        y_loc = y_loc - 200
        x_loc = x_loc + 200
    world_mask = node_tree.nodes.new('CompositorNodeIDMask')
    world_mask.location = -468.344, y_loc
    world_mix = node_tree.nodes.new('CompositorNodeMixRGB')
    world_mix.location = x_loc, y_loc
    world_mask.index = 0
    group_outputs.location = x_loc+200,y_loc
    node_tree.links.new(world_mask.inputs[0], layer.outputs['IndexMA'])
    node_tree.links.new(world_mix.inputs[0], world_mask.outputs[0])
    node_tree.links.new(world_mix.inputs[1], prev_mix.outputs[0])
    node_tree.links.new(world_mix.outputs[0], group_outputs.inputs['Mask'])
    world_mix.inputs[2].default_value = random.random(), random.random(), random.random(), 1.0
