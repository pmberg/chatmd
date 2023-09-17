import React from 'react';

function DashboardView({ subsequentMessages }) {
    return (
        <div className="dashboard-container">
            <h3>Health Insights</h3>
            <ul className="diseases-list">
                {subsequentMessages.map((message, index) => (
                    <li key={index}>
                        <span className="disease-name">{message.disease}</span>
                        <div className="probability-bar" 
                             style={{width: `${message.probability * 100}%`}}></div>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default DashboardView;

