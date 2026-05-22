import { Route, Switch } from 'wouter';
import Layout from './components/Layout';
import FrontPage from './pages/FrontPage';
import ForeignAffairs from './pages/ForeignAffairs';
import DomesticNews from './pages/DomesticNews';
import TheColonies from './pages/TheColonies';
import Commerce from './pages/Commerce';
import ArtsLetters from './pages/ArtsLetters';
import ScienceIndustry from './pages/ScienceIndustry';
import SocietyFashion from './pages/SocietyFashion';
import Classifieds from './pages/Classifieds';
import SportingNews from './pages/SportingNews';

export default function App() {
  return (
    <Layout>
      <Switch>
        <Route path="/" component={FrontPage} />
        <Route path="/foreign" component={ForeignAffairs} />
        <Route path="/domestic" component={DomesticNews} />
        <Route path="/colonies" component={TheColonies} />
        <Route path="/commerce" component={Commerce} />
        <Route path="/arts" component={ArtsLetters} />
        <Route path="/science" component={ScienceIndustry} />
        <Route path="/society" component={SocietyFashion} />
        <Route path="/classifieds" component={Classifieds} />
        <Route path="/sports" component={SportingNews} />
      </Switch>
    </Layout>
  );
}
