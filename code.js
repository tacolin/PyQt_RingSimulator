var py_obj;

jsPlumb.ready(function() {

    var instance = jsPlumb.getInstance({
            DragOptions : { cursor: 'pointer', zIndex:2000 },
            ConnectionOverlays : [
                    [ "Arrow", { location:1 } ],
                    [ "Label", { 
                            location:0.1,
                            id:"label",
                            cssClass:"aLabel"
                    }]
            ],
            Container:"flowchart"
    });		

    var connectorPaintStyle = {
            lineWidth:4,
            strokeStyle:"#61B7CF",
            joinstyle:"round",
            outlineColor:"white",
            outlineWidth:2
    };

    var connectorHoverStyle = {
            lineWidth:4,
            strokeStyle:"#216477",
            outlineWidth:2,
            outlineColor:"white"
    };

    var endpointHoverStyle = {
            fillStyle:"#216477",
            strokeStyle:"#216477"
    };

    var sourceEndpoint = {
        endpoint:"Dot",
        paintStyle:{ 
                strokeStyle:"#7AB02C",
                fillStyle:"transparent",
                radius:7,
                lineWidth:3 
        },				
        isSource:true,
        connector:[ "Flowchart", { stub:[40, 60], gap:10, cornerRadius:5, alwaysRespectStubs:true } ],
        connectorStyle:connectorPaintStyle,
        hoverPaintStyle:endpointHoverStyle,
        connectorHoverStyle:connectorHoverStyle,
        dragOptions:{},
        overlays:[
            [ 
                "Label", 
                { 
                    location:[0.5, 1.5], 
                    label:"Drag",
                    cssClass:"endpointSourceLabel" 
                } 
            ]
        ]
    };

    // the definition of target endpoints (will appear when the user drags a connection) 
    var targetEndpoint = {
        endpoint:"Dot",					
        paintStyle:{ fillStyle:"#7AB02C",radius:11 },
        hoverPaintStyle:endpointHoverStyle,
        maxConnections:-1,
        dropOptions:{ hoverClass:"hover", activeClass:"active" },
        isTarget:true,			
        overlays:[
            [ 
                "Label", 
                { 
                    location:[0.5, -0.5], 
                    label:"Drop", 
                    cssClass:"endpointTargetLabel" 
                } 
            ]
        ]
    };
    
    var init = function(connection) {			
        connection.getOverlay("label").setLabel(connection.sourceId.substr(-1) + "-" + connection.targetId.substr(-1));
        connection.bind("editCompleted", function(o) {
                if (typeof console !== "undefined") {
                    console.log("connection edited. path is now ", o.path);
                }
        });
    };			

    var _addEndpoints = function(toId, sourceAnchors, targetAnchors) {
        for (var i = 0; i < sourceAnchors.length; i++) {
            var sourceUUID = toId + sourceAnchors[i];
            instance.addEndpoint(toId, sourceEndpoint, { anchor:sourceAnchors[i], uuid:sourceUUID });						
        }
        for (var j = 0; j < targetAnchors.length; j++) {
            var targetUUID = toId + targetAnchors[j];
            instance.addEndpoint(toId, targetEndpoint, { anchor:targetAnchors[j], uuid:targetUUID });						
        }
    };

    // suspend drawing and initialise.
    instance.doWhileSuspended(function() {

        _addEndpoints("win4", ["TopCenter", "BottomCenter"], ["LeftMiddle", "RightMiddle"]);			
        _addEndpoints("win2", ["LeftMiddle", "BottomCenter"], ["TopCenter", "RightMiddle"]);
        _addEndpoints("win3", ["RightMiddle", "BottomCenter"], ["LeftMiddle", "TopCenter"]);
        _addEndpoints("win1", ["LeftMiddle", "RightMiddle"], ["TopCenter", "BottomCenter"]);

        // listen for new connections; initialise them the same way we initialise the connections at startup.
        instance.bind("connection", function(connInfo, originalEvent) { 
            init(connInfo.connection);
//            py_obj.printText("connection source id = " + connInfo.sourceId + " target id = " + connInfo.targetId + " be created");
        });			

        // make all the window divs draggable						
        instance.draggable(jsPlumb.getSelector(".flowchart .window"), { grid: [20, 20] });		

        // THIS DEMO ONLY USES getSelector FOR CONVENIENCE. Use your library's appropriate selector 
        // method, or document.querySelectorAll:
//        jsPlumb.draggable(document.querySelectorAll(".window"), { grid: [20, 20] });

        // connect a few up
//        instance.connect({uuids:["Window2BottomCenter", "Window3TopCenter"], editable:true});
//        instance.connect({uuids:["Window2LeftMiddle", "Window4LeftMiddle"], editable:true});
//        instance.connect({uuids:["Window4TopCenter", "Window4RightMiddle"], editable:true});
//        instance.connect({uuids:["Window3RightMiddle", "Window2RightMiddle"], editable:true});
//        instance.connect({uuids:["Window4BottomCenter", "Window1TopCenter"], editable:true});
//        instance.connect({uuids:["Window3BottomCenter", "Window1BottomCenter"], editable:true});

        //
        // listen for clicks on connections, and offer to delete connections on click.
        //
        instance.bind("click", function(conn, originalEvent) {
            if (confirm("Delete connection from " + conn.sourceId + " to " + conn.targetId + "?")) {
                jsPlumb.detach(conn);
//                py_obj.printText("connection source id = " + conn.sourceId + " target id = " + conn.targetId + " be deleted");
            }
        });	

        instance.bind("connectionDrag", function(connection) {
            console.log("connection " + connection.id + " is being dragged. suspendedElement is ", connection.suspendedElement, " of type ", connection.suspendedElementType);
        });		

        instance.bind("connectionDragStop", function(connection) {
            console.log("connection " + connection.id + " was dragged");
        });

        instance.bind("connectionMoved", function(params) {
            console.log("connection " + params.connection.id + " was moved");
        });
    });

});