# Function to render the FAQ content with full formatting
def get_faq_content():
    faq_html = """
    <div style="padding: 20px; font-family: Arial, sans-serif; box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);">
        <h3 style="color: #007bff; text-align: center;">Frequently Asked Questions</h3>
        <ul style="list-style-type: none; padding: 0; font-size: 14px;">
            <li><strong>Q1. Who is this software for?</strong><br>
                <p>This software is designed for Database Administrators (DBAs), developers, and other professionals who need to interact with databases. 
                It is particularly beneficial for users with little or no experience in database command-line operations, as it leverages AI to simplify 
                database management tasks.</p>
            </li>
            <br>
            <li><strong>Q2. What operations are supported?</strong><br>
                <p>The software supports the following key database operations:</p>
                <ul>
                    <li><strong>Insert:</strong> Add a new entry to the database.</li>
                    <li><strong>Update:</strong> Modify an existing entry in the database.</li>
                    <li><strong>Delete:</strong> Remove an entry from the database.</li>
                    <li><strong>Find:</strong> Retrieve a specific entry based on user input.</li>
                </ul>
                <p>Examples:</p>
                <ul>
                    <li>Insert: "Add a record for team04 with members 'a, b, c, d'."</li>
                    <li>Update: "Update the members of team04 to 'x, y, z'."</li>
                    <li>Delete: "Remove the record for team01."</li>
                    <li>Find: "Retrieve the data for case01."</li>
                </ul>
            </li>
            <br>
            <li><strong>Q3. What is the input format?</strong><br>
                <p>The input must be in text format, clearly stating:</p>
                <ul>
                    <li>The action to perform (insert, update, delete, find).</li>
                    <li>The key-value pair or data associated with the action.</li>
                </ul>
                <p>Examples:</p>
                <ul>
                    <li>Insert: "Add a record for team04 with members 'a, b, c, d'."</li>
                    <li>Update: "Update team04's members to 'x, y, z'."</li>
                    <li>Delete: "Remove the record for team01."</li>
                    <li>Find: "Retrieve the data for case01."</li>
                </ul>
            </li>
            <br>
            <li><strong>Q4. What kind of backend system is used?</strong><br>
                <p>The system uses a key-value store as the backend with fields such as:</p>
                <ul>
                    <li><strong>Key:</strong> Unique identifier for entries.</li>
                    <li><strong>Value:</strong> Associated data.</li>
                    <li><strong>Created DateTime:</strong> Timestamp of entry creation.</li>
                    <li><strong>Updated DateTime:</strong> Timestamp of last modification.</li>
                </ul>
                <p>The backend can be either in-memory (fast but temporary) or persistent (stored on disk).</p>
            </li>
            <br>
            <li><strong>Q5. How does the system ensure accuracy?</strong><br>
                <p>Structured Responses: Prompts to the LLM are designed to return structured outputs (e.g., JSON) that precisely define the intended action.</p>
                <p>Validation: The system validates parsed commands before executing them.</p>
            </li>
            <br>
            <li><strong>Q6. What if the system doesn't understand a command?</strong><br>
                <p>If the input is ambiguous or invalid:</p>
                <ul>
                    <li>The system provides feedback to clarify the issue.</li>
                    <li>It may suggest a corrected version of the input or ask for additional details.</li>
                </ul>
            </li>
            <br>
            <li><strong>Q7. What are some real-world use cases?</strong><br>
                <ul>
                    <li><strong>Database Management:</strong> Adding, updating, or deleting records in a corporate database.</li>
                    <li><strong>Automation:</strong> Simplifying repetitive data entry or updates.</li>
                    <li><strong>Education:</strong> Assisting learners in understanding database operations without requiring SQL expertise.</li>
                </ul>
            </li>
            <br>
            <li><strong>Q8. What are the system's limitations?</strong><br>
                <ul>
                    <li><strong>Complex Queries:</strong> The system is optimized for single-operation tasks and might struggle with multi-step or highly complex queries.</li>
                    <li><strong>Performance:</strong> In-memory backends may not be suitable for large-scale data.</li>
                </ul>
            </li>
            <br>
            <li><strong>Q9. How do I interact with the system?</strong><br>
                <p><strong>Web Interface:</strong> A user-friendly option, accessible via any browser. The interface guides the users through input requirements and displays results in real-time.</p>
            </li>
            <br>
            <li><strong>Q10. How is data security handled?</strong><br>
                <p>Data modifications are logged with timestamps for auditing purposes. Authentication mechanisms can be integrated to restrict access.</p>
            </li>
        </ul>
    </div>
    """
    return faq_html