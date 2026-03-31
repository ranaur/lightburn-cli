[![nuCarve Home](https://nucarve.com/wp-content/uploads/2022/12/nuCarve-logo-white-horz.svg)](https://nucarve.com/)

# Documenting the LightBurn file format

- November 27th, 2022
- No Comments

The popular commercial laser cutter/engraver software program, LightBurn, saves projects using the standard [XML](https://www.w3schools.com/xml/xml_whatis.asp) format. This means we can easily read and write the file, but the schema (the tags and attributes) is currently undocumented. That's not to say it's confidential or private, as the top dog at [LightBurn Software](https://lightburnsoftware.com/) has been [very helpful](https://forum.lightburnsoftware.com/t/is-lightburn-file-format-lbrn2-documented-or-open-sourced/56221/2) when people have asked questions about it. If you know the software, you can quickly make sense of most of it just by making a few projects and opening up the files in a text editor.

That is until you get to the `<Shape>` tag. It's the tag that defines the geometry (lines, curves, rectangles, etc.), as well as transformations like rotations, and skewing. It's also the only tag that's different between the legacy (`.lbrn`) and the current (`.lbrn2`) file formats. The `.lbrn2` format has a condensed format that is [smaller but much harder for humans to read](https://nucarve.com/lightburn-lbrn-lbrn2-file-formats), which makes the file smaller and improves loading and saving performance. This article is going to focus solely on the legacy file format, but all the concepts are the same either way.

## The back story

You might be wondering why we've spent the time figuring all this out. We've been working on a project that creates complex geometry for LightBurn and to do that we needed to understand the format in detail. In the hope that others might create and share interesting tools that automate LightBurn, we decided to share our research. Please leave a comment below if you create something using this - it would make our day!

The project we created is called [LaserPost](https://nucarve.com/laserpost), and it's a free post-processor for Fusion 360 (and other Autodesk CAM products such as HSMWorks and Inventor) that creates LightBurn project files directly from Fusion solid models using CAM. Before writing this, we would make a solid model in Fusion, usually exporting a sketch of my design as a DXF file, and then importing that into LightBurn. Then we would have to assign and adjust all my layer settings, remove any unwanted lines or shapes, adjust the kerf depending on the design, fix up engraved text, and any other adjustments needed, and then we could burn it. When we made a change to the model we would have to go back and do it again.

A better solution would be to do all this directly from CAM attached to the solid model, using tools with materials pre-configured and automatically creating the LightBurn file ready to burn, making the process simple, reliable, and consistent. So that's why we created [LaserPost](https://nucarve.com/laserpost), and why we had to dive into the file format of LightBurn!

## Introduction to `<Shape>`

The `<Shape>` tag contains all the geometry that you want to burn. It includes the grouping of shapes and the transforms (rotation, skewing, positioning, etc) for the points that make up the shape. Since it does a lot of different things, the most important attribute to start with is `Type`:

- `<Shape Type="Rect"/>`

- `<Shape Type="Path"/>`

- `<Shape Type="Group"/>`


All shapes have a `CutIndex` attribute, which specifies which layer to use (starting at 0) for the operation. The `<CutShape>` section describes all the parameters for the different layers, and the first one is index 0, the second index 1, and so on. They are pretty easy to understand just by creating a few and looking at the file, so I won't bother going into depth here.

The remaining attributes and the tags and content that follow it are specific to the type of shape and are described below.

## Matrix transforms and the `<XForm>` tag

Every shape can redefine how the coordinates within it are transformed (positioned, rotated, skewed), including nesting transforms when using groups. [Transform Matrices](https://en.wikipedia.org/wiki/Transformation_matrix) quickly get into trigonometry and a bunch of work, so unless you need to read existing files or create new ones with complex transformations, I recommend nearly (but not totally) ignoring them. If you want to learn more about how they work, you may find [this discussion](https://forum.lightburnsoftware.com/t/lbrn2-file-documentation/52174/3) helpful.

For shapes that don't need advanced transforms, simply use the identity transform. It's the matrix way of saying multiply everything by 1 ... or don't change it at all. Here is an example of a transform that keeps everything as is:

`<XForm>1 0 0 1 0 0</XForm>`

There is one type of transform you will likely need to know and use, which is how to move the base X/Y position. As long as you never use a transform that rotates or skews, you simply adjust the last two parameters. This example transforms the children by 100mm on X and 200mm on Y:

`<XForm>1 0 0 1 100 200</XForm>`

## Rectangle shapes

Perhaps the easiest-to-use shape type is `Rect`. This shape defines a simple rectangle using just width and height:

`<Shape Type="Rect" CutIndex="0" W="50" H="100" />`

Now, this rectangle won't be very useful, because it is centered around a point that starts at X=0, Y=0, which means the rectangle will have the majority of it off the usable workspace of the laser. To fix this we use a simple transform to adjust its position:

`<Shape Type="Rect" CutIndex="0" W="50" H="100">`

`  <XForm>1 0 0 1 100 200</XForm>`

`</Shape>`

This will result in a rectangle with a lower-left corner at (75, 150) and an upper-right corner at (125, 250).

Rectangle shapes have another easy-to-use feature, which is to bevel the corners with a corner radius. For example, here is a square of 100mm by 100mm with 5mm rounded corners centered at 50, 50 (resulting in the lower-left corner being at 0,0):

`<Shape Type="Rect" CutIndex="0" W="50" H="50" Cr="5">
<XForm>1 0 0 1 50 50</XForm>
</Shape>`

## Ellipse shapes

Another simple shape is `Ellipse`. This creates circles or ellipses using a center point and an X and Y radius:

`<Shape Type="Ellipse" CutIndex="0" Rx="25" Ry="50">
<XForm>1 0 0 1 50 100</XForm>
</Shape>`

The above creates an ellipse that is 50mm wide, 100mm high, and centered at 50mm by 100mm. If you want to make a circle, just set `Rx` and `Tx` to the same radius. Easy peasy.

## Polygon shapes

The "`Polygon`" shape is very similar to "`Ellipse`", with the only notable difference being you can define the number of sides on the polygon with the "`N`" attribute:

`<Shape Type="Polygon" CutIndex="1" Rx="50" Ry="50" N="6">
<XForm>1 0 0 1 100 100</XForm>
</Shape>`

## Linear path shapes

Now, this is where things start to get interesting. The `Path` shape provides for shapes ranging from simple to complex. The best place to start is with linear paths (paths where all lines are straight with no curves). You don't actually need anything other than an identity transformation matrix, because all coordinates are specified in the shape. Here is an example of a 50mmby 100mm rectangle with the lower-left corner at (0, 0):

`<Shape Type="Path" CutIndex="0">
<XForm>1 0 0 1 0 0</XForm>
<V vx="0" vy="0"/>
<V vx="0" vy="100"/>
<V vx="50" vy="100"/>
<V vx="50" vy="0"/>
<P T="L" p0="0" p1="1"/>
<P T="L" p0="1" p1="2"/>
<P T="L" p0="2" p1="3"/>
<P T="L" p0="3" p1="0"/>
</Shape>`

This shape type introduces two new tags:

- `<V>`: This defines a point, or vertex, with a position relative to the prior transformations. `vx` and `vy` specify the coordinates of the point.

- `<P>`: This defines a line (or curve) called a primitive that connects two vertices. `p0` specifies the starting vertex (the first vertex is 0), and `p1` is the ending vertex. `T` is the type of the primitive, which in this case is `"L"` for line, meaning it is straight and not a Bezier curve. You can connect vertices out of order, though they can be connected in any order.


Notice that the last primitive connects the vertex at index 3 with the starting vertex at index 0. This closes the rectangle and allows for layer types like fill to work.

The following is the exact same shape, but this time using a simple transformation setting the center point of the rectangle and using coordinates that are relative to that transformation. It's still a 50mm by 100mm rectangle with the lower-left corner at (0, 0):

`<Shape Type="Path" CutIndex="0">
<XForm>1 0 0 1 25 50</XForm>
<V vx="-25" vy="-50"/>
<V vx="-25" vy="50"/>
<V vx="25" vy="50"/>
<V vx="25" vy="-50"/>
<P T="L" p0="0" p1="1"/>
<P T="L" p0="1" p1="2"/>
<P T="L" p0="2" p1="3"/>
<P T="L" p0="3" p1="0"/>
</Shape>`

## Bezier path shapes

Of course, being limited to just straight lines gets boring fast, and shape type `Path` has another trick up its sleeve. You can define your vertices and the primitives that connect them using [Bezier curves](https://en.wikipedia.org/wiki/B%C3%A9zier_curve). If you are just using static (pre-defined) shapes, an easy way to do this is to make the shape in LightBurn with its starting position at (0,0). Save the shape using the "`.lbrn`" (legacy) format, and use that along with `<XForm>` to position it where you want.

But assuming you want to create your own curves, you will need to dive into the math behind Bezier curves. A great place to get an introduction to Bezier curves is this [interactive tutorial](https://javascript.info/bezier-curve). I also found some excellent JavaScript source code to use from [this library](https://github.com/colinmeinke/svg-arc-to-cubic-bezier) for converting simple arcs to Bezier control points (it's a fragment from the larger [svgpath](https://github.com/fontello/svgpath) library).

The idea here isn't hard. For any vector, you can have a Bezier control point that defines how a primitive should bend upon leaving the point, as well as how it should bend upon entering it. Oz over at [LightBurn](https://lightburnsoftware.com/) wrote up a nice [description](https://forum.lightburnsoftware.com/t/lbrn-or-lbrn2-xml-file-docuumentation/42317/7), which includes this visual aid:

![Graphic showing a circle made from four Bezier curves.](https://nucarve.com/wp-content/uploads/2022/11/LB-bezier.png)

The idea here is that the curve goes from V → C0 on vertex 0 to C1 → V on vertex 2, then from V → C1 on vertex 2 to V → C0 on vertex 3, and so on.

Here is an example of a 50mm circle using Bezier curves:

`<Shape Type="Path" CutIndex="1">
<XForm>1 0 0 1 50 50</XForm>
<V vx="25" vy="0" c0x="25" c0y="-13.807117" c1x="25" c1y="13.807117"/>
<V vx="0" vy="-25" c0x="-13.807117" c0y="-25" c1x="13.807117" c1y="-25"/>
<V vx="-25" vy="0" c0x="-25" c0y="13.807117" c1x="-25" c1y="-13.807117"/>
<V vx="0" vy="25" c0x="13.807117" c0y="25" c1x="-13.807117" c1y="25"/>
<P T="B" p0="0" p1="1"/>
<P T="B" p0="1" p1="2"/>
<P T="B" p0="2" p1="3"/>
<P T="B" p0="3" p1="0"/>
</Shape>`

Notice that each primitive uses "`B`" (for Bezier), and that the last primitive is connecting the last vertex to the first vertex. This means that "`c1x`" and `"c1y`" on the first vertex are defining the end of the curve for the primitive that started on the last vertex.

Lines and Bezier curves can be freely mixed to create very complex geometries:

`<Shape Type="Path" CutIndex="0">
<XForm>1 0 0 1 0 0</XForm>
<V vx="10" vy="10"/>
<V vx="60" vy="10" c0x="100" c0y="10" />
<V vx="100" vy="70" c0x="100" c0y="90" c1x="100" c1y="40" />
<V vx="70" vy="100" c1x="100" c1y="100"/>
<V vx="50" vy="120" />
<P T="L" p0="0" p1="1"/>
<P T="B" p0="1" p1="2"/>
<P T="B" p0="2" p1="3"/>
<P T="L" p0="3" p1="4"/>
</Shape>`

Here we have a straight line, moving into a couple of curves and ending with another straight line.

## Group shapes

Another useful feature of `<Shape>` is that it can group many shapes together. A shape with a type of "`Group`" can contain children with more shapes, including more groups. A group can also contain a transform, and all children will be affected by the transform... so unless you are doing matrix transformation calculations everywhere, I'd recommend making sure to use only the identity transform for groups:

`<Shape Type="Group">
<XForm>1 0 0 1 0 0</XForm>
<Children>
    <!-- shapes including groups -->
</Children>
</Shape>`

## Text shapes

I haven't had a need to use the "`Text`" yet, so I've not spent the energy to understand it. It doesn't look very hard, as a simple text shape looks like this:

`<Shape Type="Text" CutIndex="0" Font="Arial,-1,100,5,50,0,0,0,0,0" Str="Sample Text" H="25.000065" LS="0" LnS="0" Ah="0" Av="2" Weld="1" HasBackupPath="0">
<XForm>1 0 0 1 0 0</XForm>
</Shape>`

This is pretty much like the other shapes, using `<XForm>` to translate the shape, and attributes on the `<Shape>` to define the type, font, text, and some other parameters that would need to be figured out. If you save a file, it will come with a `<BackupShape>` (and the attribute "`HasBackupPath`" will be set to "`1`"). That appears to be the text rendered as a path shape using the systems fonts, and my guess is it's a backup in case the font can't be found. By changing "`HasBackupPath`" to "`0`", and removing all those paths, the file loads just fine (assuming you have the font). If you learn more about this shape, I'd be glad to update the document with more details if you leave a comment!

## Comments and thumbnails

A couple of other things that might be worth knowing, even though they aren't about shapes themselves. Notice in that last example the use of an XML comment, which can be freely added throughout the file:

`<!-- Any comment you want to make -->`

Consistent with the XML standard, these can span multiple lines, and can be useful to describe the intent of the shape(s) being generated:

`<!-- Construct a securing point for the top:`

`  Rectangle with center at [32mm, 10mm], with 8mm width and 12mm height.`

`  Using layer 3 (Engrave)`

`-->`

However, there appears to be an issue if you insert a lot of comments before to the `<Thumbnail>` tag that causes LightBurn to crash (or at least get very unhappy). I recommend injecting your headers first and doing your comments after the thumbnail.

And speaking of the thumbnail, if you want to provide one (so you can see an image before opening the file), it's simply a 250x250 pixel PNG file that has been encoded as Base64. If you want to use a static image (instead of a graphic you generate dynamically), this [free online tool](https://base64.guru/converter/encode/image/png) has worked great for me to do the conversion. Just upload the PNG, and paste the resulting Base64 into the `Source` attribute.

## Reference implementation

Our implementation of [Laserpost (a Fusion 360 / HSMWorks / Inventor post-processor for LightBurn)](https://nucarve.com/laserpost) is available on [GitHub](https://github.com/nuCarve/laserpost). It's well-commented and is licensed under the permissive MIT license. You can use it as a reference example, or even modify or reuse as much of it as you wish.

If you identify anything inaccurate or have some special knowledge that can help fill in a gap, please leave a comment and we'll fix it. Good luck on your journey, and we hope to see your amazing project soon!

Copyright © 2023 nuCarve
