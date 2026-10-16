package pe.edu.pe.PharmaBackend.security;

import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import pe.edu.pe.PharmaBackend.entity.Rol;
import pe.edu.pe.PharmaBackend.enums.Permiso;
import java.util.*;

public final class PermisosPorRol {
    private static final Map<String, Set<Permiso>> PERMISOS = Map.of(
            "ADMIN", Collections.unmodifiableSet(EnumSet.allOf(Permiso.class)),
            "VENDEDOR", Collections.unmodifiableSet(EnumSet.of(
                    Permiso.CATALOGO_LEER,
                    Permiso.CLIENTES_LEER,
                    Permiso.CLIENTES_ESCRIBIR,
                    Permiso.VENTAS_LEER,
                    Permiso.VENTAS_REGISTRAR)),

            "ALMACENERO", Collections.unmodifiableSet(EnumSet.of(
                    Permiso.CATALOGO_LEER,
                    Permiso.CATALOGO_ESCRIBIR))

    );
    private PermisosPorRol() {
    }
    public static Set<Permiso> de(String nombreRol) {
        return PERMISOS.getOrDefault(nombreRol, Set.of());
    }
    public static List<String> permisos(Collection<Rol> roles) {
        Set<String> nombres = new TreeSet<>();
        roles.forEach(rol -> de(rol.getNombre())
                .forEach(permiso -> nombres.add(permiso.name())));
        return new ArrayList<>(nombres);
    }
    public static List<GrantedAuthority> authorities(Collection<Rol> roles) {
        List<GrantedAuthority> authorities = new ArrayList<>();
        roles.stream()
                .map(Rol::getNombre)
                .sorted()
                .forEach(nombre -> authorities.add(new SimpleGrantedAuthority("ROLE_" + nombre)));
        permisos(roles).forEach(permiso ->
                authorities.add(new SimpleGrantedAuthority(permiso)));
        return authorities;
    }
}