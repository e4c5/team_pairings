import React, { useEffect, useState } from 'react';

/**
 * JQuery modal dialog
 * @param {*} props 
 * @returns 
 */
export function Confirm(props) {

    const display = {display: props.display ? 'block' : 'none'}
    
    return (
        <div className={`modal show fade` } style={display}
                data-testid="exampleModal" tabIndex="-1" 
                aria-labelledby="exampleModalLabel" aria-hidden="true">
            <div className="modal-dialog">
                <div className="modal-content">
                    <div className="modal-header">
                        <h1 className="modal-title fs-5" id="exampleModalLabel">Confirm delete</h1>
                        <button type="button" onClick={e => props.setModal(false)}
                            className="btn-close" data-bs-dismiss="modal" aria-label="Close">
                        </button>
                    </div>
                    <div className="modal-body">
                        You are about to delete all results in a round, this cannot be undone. 
                        Please type your username in the box below and hit confirm if you want
                        to proceed.
                    </div>
                    <div>
                        <input type='text' className='form-control' 
                            placeholder='Type your username here'
                            value={props.code} onChange={props.onCodeChange}/>
                    </div>
                    <div className="modal-footer">
                        <button type="button" className="btn btn-danger" onClick={props.confirmDelete}
                            data-bs-dismiss="modal">Confirm
                        </button>
                        <button type="button" className="btn btn-primary" 
                            onClick={e => props.setModal(false)}>Cancel
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}