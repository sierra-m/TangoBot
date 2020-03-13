import { Draggable, Droppable } from "react-beautiful-dnd";
import React from "react";
import Card from 'react-bootstrap/Card'

import '../style/droppables.css'

const grid = 16;

const getItemStyle = (isDragging, draggableStyle) => ({
  // some basic styles to make the items look a bit nicer
  userSelect: "none",
  padding: grid * 2,
  margin: `0 0 ${grid}px 0`,

  // change background colour if dragging
  background: isDragging ? "lightgreen" : "grey",

  // styles we need to apply on draggables
  ...draggableStyle
});

/*const getListStyle = isDraggingOver => ({
  background: isDraggingOver ? "lightblue" : "lightgrey",
  padding: grid,
  width: 250
});*/

const listStyle = {
  width: '15rem'
};

function Copyable(props) {
  return (
    <Droppable droppableId={props.droppableId} isDropDisabled={true}>
      {(provided, snapshot) => (
        <Card
          {...provided.droppableProps}
          ref={provided.innerRef}
        >
          <Card.Body>
            <Card.Title>
              Actions
            </Card.Title>
            {props.items.map((item, index) => (
              <Draggable key={item.id} draggableId={item.id} index={index}>
                {(provided, snapshot) => (
                  <React.Fragment>
                    <Card
                      bg={'info'}
                      text={'white'}
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      {...provided.dragHandleProps}
                      className={'m-2'}
                    >
                      <Card.Body>
                        {item.label}
                      </Card.Body>
                    </Card>
                    {snapshot.isDragging && (
                      <Card
                        bg={'info'}
                        text={'white'}
                        className="m-2">
                        <Card.Body>
                          {item.label}
                        </Card.Body>
                      </Card>
                    )}
                  </React.Fragment>
                )}
              </Draggable>
            ))}
            {provided.placeholder}
          </Card.Body>
        </Card>
      )}
    </Droppable>
  );
}

export default Copyable