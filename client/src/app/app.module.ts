import { NgModule, APP_INITIALIZER } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { RouterModule } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { MenuComponent } from './menu/menu.component';
import { GameComponent } from './game/game.component';
import { WebsocketService } from './shared/services/websocket.service';
import { Environment, set_environment } from './shared/env';
import { map, Observable } from 'rxjs';

function init_app(http: HttpClient): () => Observable<Environment> {
  return () => http.get<Environment>("./env.json").pipe(map(e => {
    set_environment(e)
    return e;
  }))
}

@NgModule({
  declarations: [
    AppComponent,
    MenuComponent,
    GameComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    RouterModule.forRoot([
      { path: 'menu', component: MenuComponent },
      { path: 'game', component: GameComponent },
      { path: '', redirectTo: '/menu', pathMatch: 'full' }
    ])
  ],
  providers: [
    WebsocketService,
    {
      provide: APP_INITIALIZER,
      useFactory: init_app,
      deps: [HttpClient],
      multi: true
    }],
  bootstrap: [AppComponent]
})
export class AppModule { }
