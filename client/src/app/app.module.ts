import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { RouterModule } from '@angular/router';

import { AppComponent } from './app.component';
import { MenuComponent } from './menu/menu.component';
import { GameComponent } from './game/game.component';

@NgModule({
  declarations: [
    AppComponent,
    MenuComponent,
    GameComponent
  ],
  imports: [
    BrowserModule,
    RouterModule.forRoot([
      {path: 'menu', component: MenuComponent},
      {path: 'game/:game-id', component: GameComponent},
      {path: '', redirectTo: '/menu', pathMatch: 'full'}
    ])
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
