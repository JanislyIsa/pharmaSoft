package pe.edu.pe.PharmaBackend.security;

import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.JwtException;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import pe.edu.pe.PharmaBackend.entity.Rol;
import java.util.List;
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class JwtServiceTest {
    private static final String SECRET = "w9Z6dP/dzykNH/uiI3Z/KGjBlP0H4Ji+Tuq4fm2cTNuLD4jWafu1gBL74V2SJEvy";
    private static final String OTHER_SECRET = "q8Bx3mN0vRk7TzYp1LcW5aHs9JdFg2Ue4OiPlKjMnBvCxZaSdFgHjKlQwErTyUiO";
    private final JwtService jwt = new JwtService(SECRET, 60);
    private UserDetails vendedor() { return User.withUsername("vendedor").password("irrelevante").authorities(PermisosPorRol.authorities(List.of(new Rol(2L,"VENDEDOR",null)))).build(); }

    @Test @DisplayName("El token incluye el usuario y los permisos") void generarYLeerToken() {
        String token=jwt.generarToken(vendedor()); var claims=jwt.leerClaims(token);
        assertThat(token.split("\\.")).hasSize(3);
        assertThat(claims.getSubject()).isEqualTo("vendedor");
        assertThat(claims.getExpiration()).isAfter(claims.getIssuedAt());
        assertThat(claims.get("authorities",List.class)).contains("ROLE_VENDEDOR","VENTAS_REGISTRAR").doesNotContain("REPORTES_VER");
        assertThat(jwt.extraerUsername(token)).isEqualTo("vendedor");
    }
    @Test @DisplayName("Rechaza un token alterado") void tokenAlterado() {
        String token=jwt.generarToken(vendedor()); String altered=token.substring(0,token.length()-2)+(token.endsWith("AA")?"BB":"AA");
        assertThatThrownBy(()->jwt.extraerUsername(altered)).isInstanceOf(JwtException.class);
    }
    @Test @DisplayName("Rechaza un token firmado con otra clave") void otraClave() {
        String foreign=new JwtService(OTHER_SECRET,60).generarToken(vendedor());
        assertThatThrownBy(()->jwt.extraerUsername(foreign)).isInstanceOf(JwtException.class);
    }
    @Test @DisplayName("Rechaza un token vencido") void vencido() {
        String expired=new JwtService(SECRET,-1).generarToken(vendedor());
        assertThatThrownBy(()->jwt.extraerUsername(expired)).isInstanceOf(ExpiredJwtException.class);
    }
    @Test void expiracionEnSegundos(){assertThat(jwt.getExpiracionSegundos()).isEqualTo(3600);}
}
