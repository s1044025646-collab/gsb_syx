import React, { memo } from "react";
import { Link } from "react-router-dom";

function NoteCard({note}) {
    return (
        <div className="noteCard">
            <h2 className="title">
                <Link to={`/details/${note._id}`} style={{textDecoration: 'none', color: '#f5400f'}}>{note.title}</Link>
                <Link to={`/details/${note._id}`} style={{color: '#f5400f'}}><i className="fa-solid fa-ellipsis-vertical"></i></Link>
            </h2>
            <p className="details">
                {note.details}
            </p>
        </div>
    );
}

export default memo(NoteCard, (prev, next) => {
    return prev.note._id === next.note._id &&
           prev.note.title === next.note.title &&
           prev.note.details === next.note.details;
});
