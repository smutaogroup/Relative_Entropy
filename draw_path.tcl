# draw a path for series number
# VMD
#

proc draw_path {molid color radius radius2 args} {
	puts "MolID $molid"
	puts "Color $color"
	puts "Bond Radius $radius"
	puts "Sphere Radius $radius2"

	set le [expr [llength $args]-1]


	if {$le <= 1} {
		puts "need more than 1arguments"
	} else {
		puts "Total $le Arguments"
	}

	for {set i 0} {$i < $le} {incr i} {
		set m [lindex $args $i]
		set n [lindex $args [expr $i+1]]
		puts "Path Between $m $n"
		
		draw color $color
		# residues already increased by 1
		# set rm [expr $m+1]
		# set rn [expr $n+1] 

		set resm [atomselect $molid "residue $m and name CA"]
		set resn [atomselect $molid "residue $n and name CA"]
		set corm [lindex [$resm get {x y z}] 0]
		set corn [lindex [$resn get {x y z}] 0]

		draw cylinder $corm $corn radius $radius resolution 20
		draw sphere $corm radius $radius2 resolution 20
		draw sphere $corn radius $radius2 resolution 20
	}

	 
}

