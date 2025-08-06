describe('Legal theory approval flow', () => {
  beforeEach(() => {
    cy.intercept('GET', '/api/theories/suggest', {
      statusCode: 200,
      body: { status: 'ok', theories: [{ cause: 'Test Cause', score: 0.8, elements: [] }] }
    }).as('suggest1');
    cy.visit('index.html');
    cy.contains('Case Theory').click();
    cy.wait('@suggest1');
  });

  it('approves a theory', () => {
    cy.intercept('POST', '/api/theories/accept', { statusCode: 200, body: { status: 'ok' } }).as('accept');
    cy.intercept('GET', '/api/theories/suggest', { statusCode: 200, body: { status: 'ok', theories: [] } }).as('suggest2');
    cy.contains('Approve').click();
    cy.wait('@accept');
    cy.wait('@suggest2');
  });

  it('rejects a theory', () => {
    cy.intercept('POST', '/api/theories/reject', { statusCode: 200, body: { status: 'ok' } }).as('reject');
    cy.intercept('GET', '/api/theories/suggest', { statusCode: 200, body: { status: 'ok', theories: [] } }).as('suggest3');
    cy.contains('Reject').click();
    cy.wait('@reject');
    cy.wait('@suggest3');
  });

  it('comments on a theory', () => {
    cy.window().then(win => cy.stub(win, 'prompt').returns('Looks good'));
    cy.intercept('POST', '/api/theories/comment', { statusCode: 200, body: { status: 'ok' } }).as('comment');
    cy.intercept('GET', '/api/theories/suggest', { statusCode: 200, body: { status: 'ok', theories: [] } }).as('suggest4');
    cy.contains('Comment').click();
    cy.wait('@comment');
    cy.wait('@suggest4');
  });
});
