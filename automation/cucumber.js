import { setWorldConstructor } from '@cucumber/cucumber';

// No custom world is strictly necessary for this test suite as 
// Playwright-BDD's default world provides the 'page' fixture.
// If you needed custom setup/teardown or shared state across steps,
// you would define a custom world class and use setWorldConstructor.

// Example of a custom world (if needed in the future):
// import { MyWorld } from './my_world';
// setWorldConstructor(MyWorld);
