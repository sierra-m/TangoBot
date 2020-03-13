import { Draggable, Droppable } from "react-beautiful-dnd";
import React from "react";
import Image from 'react-bootstrap/Image'

import icon from '../images/trash.png'

function Trash(props) {
  return (
    <Droppable droppableId="trash">
      {(provided, snapshot) => (
        <Image
          {...provided.droppableProps}
          ref={provided.innerRef}
          src={icon}
          thumbnail
        />
      )}
    </Droppable>
  );
}

export default Trash