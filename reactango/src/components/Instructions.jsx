import { Draggable, Droppable } from "react-beautiful-dnd";
import React, {Component} from "react";
import Card from 'react-bootstrap/Card'

import '../style/droppables.css'
import Button from "react-bootstrap/Button";
import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Spinner from 'react-bootstrap/Spinner'
import ButtonToolbar from "react-bootstrap/ButtonToolbar";
import ButtonGroup from "react-bootstrap/ButtonGroup";

const grid = 8;

const getItemStyle = (isDragging, draggableStyle) => ({
  // some basic styles to make the items look a bit nicer
  userSelect: 'none',
  padding: grid * 2,
  margin: `0 ${grid}px 0 0`,

  // change background colour if dragging
  background: isDragging ? 'lightgreen' : 'grey',

  // styles we need to apply on draggables
  ...draggableStyle,
});

const getListStyle = isDraggingOver => ({
  background: isDraggingOver ? 'lightblue' : 'lightgrey',
  display: 'flex',
  padding: grid,
  overflow: 'auto',
});

class Instructions extends Component {
  constructor (props) {
    super(props);
    this.props = props;
    this.state = {
      spinnerVisible: false,
      rerender: null
    }
  }

  showSpinner = () => {
    this.setState({spinnerVisible: true});
    setTimeout(this.hideSpinner, 5000)
  };

  hideSpinner = () => {
    this.setState({spinnerVisible: false})
  };

  increaseValue = (item) => {
    let incBy = 100;
    if (item.type === 'DR' || item.type === 'STL' || item.type === 'STR' || item.type === 'WT') {
      incBy = 250;
    } else if (item.type === 'HT' || item.type === 'HS') {
      incBy = 500;
    }
    item.value = Math.min(Math.max(item.value + incBy, item.min), item.max);
    this.setState({rerender: Math.random()})
  };

  play = () => {
    this.showSpinner();
    let out = '';
    let dir, delay;
    for (let item of this.props.items) {
      switch (item.type) {
        case 'DR':
          dir = item.value < 0 ? '-': '';
          out += item.instruction.replace('{{dir}}', dir).replace('{{delay}}', Math.abs(item.value).toString());
          break;
        case 'STL':
          out += item.instruction.replace('{{dir}}', '').replace('{{delay}}', Math.abs(item.value).toString());
          break;
        case 'STR':
          out += item.instruction.replace('{{dir}}', '-').replace('{{delay}}', Math.abs(item.value).toString());
          break;
        default:
          out += item.instruction.replace('{{dir}}', item.value.toString())
      }
    }
    console.log(out);
    fetch(`/run?instructions=${out}`);
  };

  decreaseValue = (item) => {
    let decBy = 100;
    if (item.type === 'DR' || item.type === 'STL' || item.type === 'STR' || item.type === 'WT') {
      decBy = 250;
    } else if (item.type === 'HT' || item.type === 'HS') {
      decBy = 500;
    }
    item.value = Math.min(Math.max(item.value - decBy, item.min), item.max);
    this.setState({rerender: Math.random()})
  };

  render() {
    return (
      <Droppable droppableId="instructions" direction="horizontal">
        {(provided, snapshot) => (
          <Card>
            <Card.Body>
              <Card.Title>Instructions</Card.Title>
              <Container fluid>
                <Row>
                  <Col>
                    <div
                      {...provided.droppableProps}
                      ref={provided.innerRef}
                      style={getListStyle(snapshot.isDraggingOver)}
                    >
                      {this.props.items.map((item, index) => (
                        <Draggable key={item.id} draggableId={item.id} index={index}>
                          {(provided, snapshot) => (
                            <Card
                              rerender={this.state.rerender}
                              border={'info'}
                              bg={'white'}
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              style={getItemStyle(
                                snapshot.isDragging,
                                provided.draggableProps.style
                              )}
                            >
                              {item.label}
                              <ButtonToolbar className={'mt-3'}>
                                <ButtonGroup className={'ml-2'} text={'white'}>
                                  <Button variant={'success'} onClick={() => this.increaseValue(item)}>+</Button> <Button variant={'danger'} onClick={() => this.decreaseValue(item)}>-</Button>
                                </ButtonGroup>
                              </ButtonToolbar>
                              <Card.Text>
                                {item.value}
                              </Card.Text>
                            </Card>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </div>
                  </Col>
                  <Col xs={2}>
                    <Row>
                      <Col>
                        <Button variant="outline-success" className={'ml-2 d-inline'} onClick={this.play}>Play</Button>
                      </Col>
                      <Col>
                        {this.state.spinnerVisible && <Spinner className={'m-2'} animation="border" variant="success" />}
                      </Col>
                    </Row>
                  </Col>
                </Row>
              </Container>
            </Card.Body>
          </Card>

        )}
      </Droppable>
    );
  }
}

export default Instructions