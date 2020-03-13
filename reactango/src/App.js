import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { v4 as uuid } from "uuid";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import Instructions from './components/Instructions'
import Toolbar from './components/Toolbar'
import Trash from './components/Trash'
import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'

import "./styles.css";


const COLLECTION = [
  { id: uuid(), label: "Drive", instruction: "DR{{dir}}500DEL{{delay}}DR0", value: 1000, min: -10000, max: 10000, type: 'DR' },
  { id: uuid(), label: "Turn Left", instruction: "ST{{dir}}300DEL{{delay}}ST0", value: 1000, min: 0, max: 5000, type: 'STL' },
  { id: uuid(), label: "Turn Right", instruction: "ST{{dir}}300DEL{{delay}}ST0", value: 1000, min: 0, max: 5000, type: 'STR' },
  { id: uuid(), label: "Waist Turn", instruction: "WT{{dir}}", value: 0, min: -1000, max: 1000, type: 'WT' },
  { id: uuid(), label: "Head Tilt", instruction: "HT{{dir}}", value: 0, min: -1000, max: 1000, type: 'HT' },
  { id: uuid(), label: "Head Swivel", instruction: "HS{{dir}}", value: 0, min: -1000, max: 1000, type: 'HS' }
];

const reorder = (list, startIndex, endIndex) => {
  const [removed] = list.splice(startIndex, 1);
  list.splice(endIndex, 0, removed);
  return list;
};

const copy = (source, destination, droppableSource, droppableDestination) => {
  const item = source[droppableSource.index];
  destination.splice(droppableDestination.index, 0, { ...item, id: uuid() });
  return destination;
};

const remove = (list, sourceIndex) => {
  const [removed] = list.splice(sourceIndex, 1);
  console.log(removed);
  console.log('REMOVING');
  return list;
};

function App() {
  const [instructionItems, setInstructionItems] = React.useState([]);
  const onDragEnd = React.useCallback(
    result => {
      const { source, destination } = result;

      if (!destination) {
        return;
      }

      console.log(`SOURCE: ${source.droppableId}`);
      console.log(`DEST: ${destination.droppableId}`);
      if (destination.droppableId === 'trash') {
        if (source.droppableId === 'instructions') {
          setInstructionItems(state =>
            remove(state, source.index)
          );
        }
      } else {
        switch (source.droppableId) {
          case destination.droppableId:
            setInstructionItems(state =>
              reorder(state, source.index, destination.index)
            );
            break;
          case "toolbar":
            setInstructionItems(state =>
              copy(COLLECTION, state, source, destination)
            );
            break;
          default:
            break;
        }
      }
    },
    [setInstructionItems]
  );
  return (
    <div className="App">
      <Container>
        <DragDropContext onDragEnd={onDragEnd}>
          <Row className="align-items-center mt-4">
            <Col xs={3}>
              <Toolbar items={COLLECTION} />
              <Trash/>
            </Col>
            <Col>
              <Instructions items={instructionItems} />
            </Col>
          </Row>
        </DragDropContext>
      </Container>
    </div>
  );
}

export default App;
