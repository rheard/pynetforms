# pynetforms
A Pythonic entry point for the .NET Forms libraries.

The two major UI libraries for Python are Qt and Tkinter. This library serves as an alternative, allowing for the use
    of .NET Forms in a Python-friendly manner.

### Converting Forms
The code can be quite close to the C# code, or optionally can be more closer to Python. For instance, 
    consider the following autogenerated `InitializeComponent` for a very simple form with a button that does nothing:
```csharp
private void InitializeComponent()
{
    this.button1 = new System.Windows.Forms.Button();
    this.SuspendLayout();
    // 
    // button1
    // 
    this.button1.Location = new System.Drawing.Point(12, 12);
    this.button1.Name = "button1";
    this.button1.Size = new System.Drawing.Size(75, 23);
    this.button1.TabIndex = 0;
    this.button1.Text = "button1";
    this.button1.UseVisualStyleBackColor = true;
    // 
    // Form1
    // 
    this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
    this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
    this.ClientSize = new System.Drawing.Size(800, 450);
    this.Controls.Add(this.button1);
    this.Name = "Form1";
    this.Text = "Form1";
    this.ResumeLayout(false);
}
```

This can be converted to a .NET form in Python by converting the class/method definitions to Python, remove semicolons,
    use class definitions from the netforms module, title-case booleans and convert floats from 6F to 6:
```python
import netforms

class MyForm(netforms.Form):
    def InitializeComponent(self):
        self.button1 = netforms.controls.Button()
        self.SuspendLayout()
        # 
        # button1
        # 
        self.button1.Location = netforms.drawing.Point(12, 12)
        self.button1.Name = "button1"
        self.button1.Size = netforms.drawing.Size(75, 23)
        self.button1.TabIndex = 0
        self.button1.Text = "button1"
        self.button1.UseVisualStyleBackColor = True
        # 
        # Form1
        # 
        self.AutoScaleDimensions = netforms.drawing.Size(6, 13)
        self.AutoScaleMode = netforms.forms.AutoScaleMode.Font
        self.ClientSize = netforms.drawing.Size(800, 450)
        self.Controls.Add(self.button1)
        self.Name = "Form1"
        self.Text = "Form1"
        self.ResumeLayout(False)
```

The default `__init__` for `Form` will call `InitializeComponent`. There are a few tricks we can use though,
    for instance, `Size` and `Point` are both a `namedtuple`, so the type calls for them are entirely optional.
    
Further all C# names have an alternative Python name. For example, `button.TabIndex` is the same as `button.tab_index`.
    `InitializeComponent` takes this one step further and provides options for `initialize_component` and 
    `initialize_components`. Implementing these suggestions, we get closer to Python:
```python
class MyForm(netforms.Form):
    def initialize_components(self):
        self.button1 = netforms.controls.Button()
        self.suspend_layout()
        # 
        # button1
        # 
        self.button1.location = (12, 12)
        self.button1.name = "button1"
        self.button1.size = (75, 23)
        self.button1.tab_index = 0
        self.button1.text = "button1"
        self.button1.use_visual_style_back_color = True
        # 
        # Form1
        # 
        self.auto_scale_dimensions = (6, 13)
        self.auto_scale_mode = netforms.forms.AutoScaleMode.Font
        self.client_size = (800, 450)
        self.controls.add(self.button1)
        self.name = "Form1"
        self.text = "Form1"
        self.resume_layout(False)
```

Furthermore since this is such a simple form, and does not require any event handlers, we do not even need to create
    a subclass to accomplish this:
```python
my_form = netforms.Form(
    client_size=(800, 450),
    auto_scale_dimensions=(6, 13),
    auto_scale_mode=netforms.forms.AutoScaleMode.Font,
    name="Form1",
    text="Form1",
    controls=[netforms.controls.Button(
        location=(12, 12),
        name="button1",
        size=(75, 23),
        tab_index=0,
        text="button1",
        use_visual_style_back_color=True,
    )],
)
```
Notice that the controls can take in attributes as keyword arguments as well.

##### Running Forms
Everything from `System.Windows.Forms.Application` is available by both original and Python-friendly names. Simply
    provide `run` with a Form instance, as you would in C#:
```python
netforms.run(my_form)
```

The base `netforms` module will shadow methods from `System.Windows.Forms.Applicatoin`, meaning both `Run` and `run`
    are available.

### Events
Events work similarly to C# in that you must add a callable to the event handler. For example, lets take the simple
    form from above, and add an event handler that will make the button serve as a counter, displaying how many times
    it has been clicked.

```python
class MyForm(netforms.Form):
    def initialize_components(self):
        self.suspend_layout()
        # 
        # button1
        # 
        self.button1 = netforms.controls.Button(
            location=(12, 12),
            name="button1",
            size=(75, 23),
            tab_index=0,
            text="0",
            use_visual_style_back_color=True,
        )
        self.button1.click += self.button1_click
        # 
        # Form1
        # 
        self.auto_scale_dimensions = (6, 13)
        self.auto_scale_mode = netforms.forms.AutoScaleMode.Font
        self.client_size = (800, 450)
        self.controls.add(self.button1)
        self.name = "Form1"
        self.text = "Form1"
        self.resume_layout(False)

    def button1_click(self, sender, e):
        sender.text = int(sender.text) + 1
        sender.update()
```

First we define an event handler `button1_click`. This handler needs 2 arguments, `sender` and `e`. Notice that the 
    sender is already wrapper, allowing for usage of Python style names and implicit type conversion.
    
Next notice the line where we add `button1_click` to the EventHandler `click`. This is exactly like C# except without
    the converting to another type.

That is it! `button1_click` will be called when the button is clicked!

Optionally, event handlers can be provided in the `__init__` as well:
```python
self.button1 = netforms.controls.Button(
    ...
    click=self.button1_click,
)
```

Multiple handlers can be provided this way using an iterable
```python
self.button1 = netforms.controls.Button(
    ...
    click=[self.button1_click, self.generic_button_handler],
)
```