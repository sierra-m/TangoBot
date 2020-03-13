import React from "react";
import Copyable from './Copyable'

import '../style/droppables.css'

function Toolbar(props) {
  return <Copyable droppableId="toolbar" className="toolbar" items={props.items} />;
}

export default Toolbar